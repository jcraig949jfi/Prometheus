-- Form (d): Encounter semantics server-side in Redis Lua (5.1, doubles + bit lib).
-- KEYS: 1 regs (u16 LE, n*R) 2 charge (u32 LE, value+2^31, n*S) 3 alive (u8, n*S)
--       4 pend (u16 LE, n*(D+1)*R, amounts mod M) 5 stoch (u32 lo, u32 hi LE, n)
-- ARGV: n R S W t0 k D regime_period stoch_rate act_cost step_cost yield_reg ylo yhi
--       yield_amt skip_lin record lin_csv tgts_csv acts(u8, k*n*S*W)
-- Runs k ticks for every env (one EVALSHA per tick is k=1). record=1 returns, per env
-- per tick, R regs + S charge + S alive as a flat integer array.
local n, R, S, W = tonumber(ARGV[1]), tonumber(ARGV[2]), tonumber(ARGV[3]), tonumber(ARGV[4])
local t0, k, D = tonumber(ARGV[5]), tonumber(ARGV[6]), tonumber(ARGV[7])
local rp, srate, act_cost, step_cost = tonumber(ARGV[8]), tonumber(ARGV[9]), tonumber(ARGV[10]), tonumber(ARGV[11])
local yreg, ylo, yhi, yamt = tonumber(ARGV[12]), tonumber(ARGV[13]), tonumber(ARGV[14]), tonumber(ARGV[15])
local skip, record = tonumber(ARGV[16]), tonumber(ARGV[17])
local M = 65536
local TWO32 = 4294967296
local floor = math.floor
local band, bor, bxor, lsh, rsh = bit.band, bit.bor, bit.bxor, bit.lshift, bit.rshift
local sbyte, schar = string.byte, string.char

local function csv(s)
  local t = {}
  for x in string.gmatch(s, "[^,]+") do t[#t + 1] = tonumber(x) end
  return t
end
local lin, tgts = csv(ARGV[18]), csv(ARGV[19])
local L = #lin / 6

local function bytes(s)
  local out, c, len, i = {}, 0, #s, 1
  while i <= len do
    local j = i + 3999
    if j > len then j = len end
    local b = {sbyte(s, i, j)}
    for q = 1, #b do c = c + 1; out[c] = b[q] end
    i = j + 1
  end
  return out
end

local function pack(tb)
  local parts, i, len = {}, 1, #tb
  while i <= len do
    local j = i + 3999
    if j > len then j = len end
    parts[#parts + 1] = schar(unpack(tb, i, j))
    i = j + 1
  end
  return table.concat(parts)
end

local function u(x) if x < 0 then return x + TWO32 end return x end

local function xs(hi, lo)
  local nhi = bxor(hi, bor(lsh(hi, 13), rsh(lo, 19)))
  local nlo = bxor(lo, lsh(lo, 13))
  hi, lo = nhi, nlo
  nlo = bxor(lo, bor(rsh(lo, 7), lsh(hi, 25)))
  nhi = bxor(hi, rsh(hi, 7))
  hi, lo = nhi, nlo
  nhi = bxor(hi, bor(lsh(hi, 17), rsh(lo, 15)))
  nlo = bxor(lo, lsh(lo, 17))
  return u(nhi), u(nlo)
end

-- (hi,lo) * 0x2545F4914F6CDD1D mod 2^64, then mod m; 16-bit limbs keep products < 2^53
local function mulmod(hi, lo, m)
  local s0, s1 = lo % 65536, floor(lo / 65536)
  local s2, s3 = hi % 65536, floor(hi / 65536)
  local p0 = s0 * 0xDD1D
  local p1 = s0 * 0x4F6C + s1 * 0xDD1D + floor(p0 / 65536)
  local p2 = s0 * 0xF491 + s1 * 0x4F6C + s2 * 0xDD1D + floor(p1 / 65536)
  local p3 = s0 * 0x2545 + s1 * 0xF491 + s2 * 0x4F6C + s3 * 0xDD1D + floor(p2 / 65536)
  local r0, r1, r2, r3 = p0 % 65536, p1 % 65536, p2 % 65536, p3 % 65536
  return ((((r3 % m) * 65536 + r2) % m * 65536 + r1) % m * 65536 + r0) % m
end

local regsb = bytes(redis.call("GET", KEYS[1]))
local chb = bytes(redis.call("GET", KEYS[2]))
local alb = bytes(redis.call("GET", KEYS[3]))
local pdb = bytes(redis.call("GET", KEYS[4]))
local stb = bytes(redis.call("GET", KEYS[5]))
local acts = bytes(ARGV[20])

local D1 = D + 1
local SW = S * W
local log, lc = {}, 0
local reg, charge, alive, pend = {}, {}, {}, {}

for e = 0, n - 1 do
  local rb = e * R * 2
  for r = 0, R - 1 do reg[r] = regsb[rb + 2 * r + 1] + 256 * regsb[rb + 2 * r + 2] end
  local cb = e * S * 4
  for s = 0, S - 1 do
    local o = cb + 4 * s
    charge[s] = chb[o + 1] + 256 * chb[o + 2] + 65536 * chb[o + 3] + 16777216 * chb[o + 4] - 2147483648
    alive[s] = alb[e * S + s + 1]
  end
  local pb = e * D1 * R * 2
  for d = 0, D - 0 do
    local row = pend[d] or {}
    pend[d] = row
    for r = 0, R - 1 do
      local o = pb + (d * R + r) * 2
      row[r] = pdb[o + 1] + 256 * pdb[o + 2]
    end
  end
  local so = e * 8
  local stlo = stb[so + 1] + 256 * stb[so + 2] + 65536 * stb[so + 3] + 16777216 * stb[so + 4]
  local sthi = stb[so + 5] + 256 * stb[so + 6] + 65536 * stb[so + 7] + 16777216 * stb[so + 8]

  for t = t0, t0 + k - 1 do
    local ai = ((t - t0) * n + e) * SW
    local prow = pend[(t + D) % D1]
    for s = 0, S - 1 do
      if alive[s] == 1 then
        local base = ai + s * W
        local mag = 0
        for i = 1, W do mag = mag + acts[base + i] % 8 end
        local cost = mag * act_cost
        if cost <= charge[s] then charge[s] = charge[s] - cost end
        for i = 1, W do
          local x = acts[base + i] % 8
          if x > 0 then
            local tg = tgts[i]
            prow[tg] = (prow[tg] + x * 251) % M
          end
        end
      end
    end
    local lrow = pend[t % D1]
    for r = 0, R - 1 do
      reg[r] = (reg[r] + lrow[r]) % M
      lrow[r] = 0
    end
    if skip == 0 then
      local flip = rp > 0 and (floor(t / rp) % 2 == 1)
      for o = 0, L - 1 do
        local q = o * 6
        local a = lin[q + 2]
        if flip then a = (M - a) % M end
        reg[lin[q + 1]] = (a * reg[lin[q + 3]] + lin[q + 4] * reg[lin[q + 5]] + lin[q + 6]) % M
      end
    end
    if srate > 0 then
      sthi, stlo = xs(sthi, stlo)
      if mulmod(sthi, stlo, srate) == 0 then
        -- wforge evaluates the assignment RHS first: draw 2 = value, draw 3 = index
        sthi, stlo = xs(sthi, stlo)
        local val = mulmod(sthi, stlo, M)
        sthi, stlo = xs(sthi, stlo)
        reg[mulmod(sthi, stlo, R)] = val
      end
    end
    local v = reg[yreg]
    local inw
    if ylo < yhi then inw = (v >= ylo and v < yhi) else inw = (v >= ylo or v < yhi) end
    local nl = 0
    for s = 0, S - 1 do if alive[s] == 1 then nl = nl + 1 end end
    local share = 0
    if nl > 0 then share = floor(yamt / nl) end
    for s = 0, S - 1 do
      if alive[s] == 1 then
        charge[s] = charge[s] - step_cost
        if inw then charge[s] = charge[s] + share end
        if charge[s] <= 0 then alive[s] = 0 end
      end
    end
    if record == 1 then
      for r = 0, R - 1 do lc = lc + 1; log[lc] = reg[r] end
      for s = 0, S - 1 do lc = lc + 1; log[lc] = charge[s] end
      for s = 0, S - 1 do lc = lc + 1; log[lc] = alive[s] end
    end
  end

  for r = 0, R - 1 do
    regsb[rb + 2 * r + 1] = reg[r] % 256
    regsb[rb + 2 * r + 2] = floor(reg[r] / 256)
  end
  for s = 0, S - 1 do
    local o = cb + 4 * s
    local c = charge[s] + 2147483648
    chb[o + 1] = c % 256; c = floor(c / 256)
    chb[o + 2] = c % 256; c = floor(c / 256)
    chb[o + 3] = c % 256
    chb[o + 4] = floor(c / 256)
    alb[e * S + s + 1] = alive[s]
  end
  for d = 0, D do
    local row = pend[d]
    for r = 0, R - 1 do
      local o = pb + (d * R + r) * 2
      pdb[o + 1] = row[r] % 256
      pdb[o + 2] = floor(row[r] / 256)
    end
  end
  local lo_, hi_ = stlo, sthi
  for q = 1, 4 do stb[so + q] = lo_ % 256; lo_ = floor(lo_ / 256) end
  for q = 5, 8 do stb[so + q] = hi_ % 256; hi_ = floor(hi_ / 256) end
end

redis.call("SET", KEYS[1], pack(regsb))
redis.call("SET", KEYS[2], pack(chb))
redis.call("SET", KEYS[3], pack(alb))
redis.call("SET", KEYS[4], pack(pdb))
redis.call("SET", KEYS[5], pack(stb))
return log
