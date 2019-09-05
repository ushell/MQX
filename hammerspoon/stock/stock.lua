local XQAPI = "https://stock.xueqiu.com/v5/stock/realtime/quotec.json"
local menubar = hs.menubar.new()
local menuData = {}

local headers = {}
headers['User-Agent'] 		  = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:68.0) Gecko/20100101 Firefox/68.0'
headers['Accept-Encoding'] 	= 'gzip, deflate'
headers['Connection'] 		  = 'keep-alive'
headers['X-Forwarded-For'] 	= '73b1:1cf:e705:88ab:1'

local stockList = 'SH000001'

-- 价格阈值
local stockMonitor = {}
stockMonitor['SH000001'] = {'2960', '>='}

function updateMenubar()
    menubar:setMenu(menuData)
end

function getStock(fisrt)
	fisrt = fisrt or false

	-- 交易时间限制
	if (false == fisrt) then
		local hour = os.date("%H", os.time());
		hour = tonumber(hour)
		if (hour > 15 or hour < 9) then
			return
		end
	end

	-- 请求服务
	api = string.format("%s/?symbol=%s", XQAPI, stockList)
	hs.http.doAsyncRequest(api, "GET", nil, headers, function(code, body, htable)
	  	if code ~= 200 then
	     	print('获取数据错误:'..code)
	     	return
	  	end
	  	menuData = {}

	  	rawjson = hs.json.decode(body)
	  	for k, v in pairs(rawjson.data) do
	  		monitor(v)
	  		-- 菜单样式
	  		titles = string.format("🇨🇳%s ¥%s 🚀%s 👆%s 👇︎%s 🚗%s 💰%.3f/亿 🤝%s",
	  			v.symbol, v.current, v.percent..'%', v.high, v.low, v.open, v.amount/100000000, v.turnover_rate..'%'
	  		)
            table.insert(menuData, {title = titles})
        end    
	  	updateMenubar()	
	end)
end

function monitor(stock)
	for symbol, item in pairs(stockMonitor) do
		if (stock.symbol == symbol) then
			local price = item[1]
			local op 	= item[2]

			local message = string.format("🚨%s ¥%s", symbol, stock.current)

			if (op == '>=' and stock.current >= tonumber(price)) then
				hs.alert(message)
			end

			if (op == '<=' and stock.current >= tonumber(price)) then
				hs.alert(message)
			end
		end
	end
end

menubar:setTitle('🚨')
getStock(true)
updateMenubar()
hs.timer.doEvery(600, getStock)
