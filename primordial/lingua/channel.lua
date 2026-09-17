-- Lane D, D1 metered channel: ONE call per tick settles every env's message.
-- KEYS: 1 charge (u32 LE, one per env)  2 message stream
-- ARGV: 1 n  2 alpha_int (charge per bit)  3 tick  4 cheat (0 honest, 1 free_unaffordable, 2 undercharge)
--       5 bits (u8 per env)  6 syms (u8 per env)  7 credit (u8 per env, yield earned last tick)
-- Per env: the credit lands, then a send is charged alpha*bits if the sender can pay. A send it
-- cannot pay is NOT delivered (the receiver hears silence). The stream entry holds only what was
-- delivered. Returns {stream id, total charged, total credited, new charge string}.
local n = tonumber(ARGV[1])
local alpha = tonumber(ARGV[2])
local cheat = tonumber(ARGV[4])
local bits, syms, credit = ARGV[5], ARGV[6], ARGV[7]
local ch = redis.call('GET', KEYS[1])
local sbyte, schar, ssub, floor = string.byte, string.char, string.sub, math.floor
local out, db, ds = {}, {}, {}
local charged, credited = 0, 0
for i = 1, n do
  local o = (i - 1) * 4
  local b1, b2, b3, b4 = sbyte(ch, o + 1, o + 4)
  local c = b1 + b2 * 256 + b3 * 65536 + b4 * 16777216
  local cr = sbyte(credit, i)
  c = c + cr
  credited = credited + cr
  local nb = sbyte(bits, i)
  local deliver = false
  if nb > 0 then
    local cost = alpha * nb
    if cheat == 2 then cost = alpha * floor(nb / 2) end
    if c >= cost then
      c = c - cost
      charged = charged + cost
      deliver = true
    elseif cheat == 1 then
      deliver = true
    end
  end
  if deliver then
    db[i] = schar(nb)
    ds[i] = ssub(syms, i, i)
  else
    db[i] = '\0'
    ds[i] = '\0'
  end
  out[i] = schar(c % 256, floor(c / 256) % 256, floor(c / 65536) % 256, floor(c / 16777216) % 256)
end
local cs = table.concat(out)
redis.call('SET', KEYS[1], cs)
local id = redis.call('XADD', KEYS[2], 'MAXLEN', '~', 100000, '*',
                      't', ARGV[3], 'bits', table.concat(db), 'syms', table.concat(ds))
return {id, charged, credited, cs}
