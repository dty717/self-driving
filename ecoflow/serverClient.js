const net = require('net');
const { Console } = require('console');
const fs = require('fs');
const { comandList ,serverReq, keyCrypt, getState} = require('./commond');
const output = fs.createWriteStream('./stdout.log', { flags: 'a' });
const errorOutput = fs.createWriteStream('./stderr.log', { flags: 'a' });
// Custom simple logger
const logger = new Console({ stdout: output, stderr: errorOutput });

function sleep(time) {
    return new Promise(resolve => setTimeout(resolve, time));
}
logger.log('\r\n\r\n\r\n')

var config = { host: "120.77.176.146", port: 6500 }
var needStop = false
// var functionType = "listen"
var functionType = "testClient"
// var functionType = "testClientLimitTimes"
// var functionType = "testServer"
// setTimeout(() => {
//     setInterval(()=>{
//         _c.write(serverReq.state)
//     },1000)
// }, 4000);
var delayTime = 0
var limitTimes = 0
var limitMaxTimes = 3
var temBuf = []
var stateRegex = /aa02\w{4}832f(\w\w)\w\w0000ffff02202002(\w{222})(\w{4})/
const server = net.createServer((c) => {
    console.log('client connected:' + c.remoteAddress);

    var client
    if (functionType == "testServer") {
        client = net.createConnection(config, () => {
            // 'connect' listener.
            console.log('connected to server!');
        });
        _client = client
        client.on('data', async (data) => {
            logger.log('server', data.toString('hex'));
            console.log('server', data.byteLength);
        });
        client.on('end', () => {
            console.log('disconnected from server');
        });
    }
    else if (functionType == "testClient") {
        client = net.createConnection(config, () => {
            // 'connect' listener.
            console.log('connected to server!');
        });
        _client = client
        client.on('data', async (data) => {
            logger.log('server', data.toString('hex'));
            // console.log('server', data.byteLength);
            await sleep(delayTime)
            await c.write(data)
        });
        client.on('end', () => {
            console.log('disconnected from server');
        });

    }
    // var functionType = "testClientLimitTimes"
    else if (functionType == "testClientLimitTimes") {
        client = net.createConnection(config, () => {
            // 'connect' listener.
            console.log('connected to server!');
        });
        _client = client
        client.on('data', async (data) => {
            // logger.log('server', data.toString('hex'));
            console.log('server', data.byteLength);
            if (limitTimes < limitMaxTimes) {
                await sleep(delayTime)
                if (!needStop) {
                    await c.write(data)
                }
            }
        });
        client.on('end', () => {
            console.log('disconnected from server');
        });
    }

    else if (functionType == "listen") {
        client = net.createConnection(config, () => {
            // 'connect' listener.
            console.log('connected to server!');
        });
        _client = client
        client.on('data', async (data) => {
            logger.log('server', data.toString('hex'));
            console.log('server', data.byteLength);
            await sleep(delayTime)
            if (!needStop) {
                await c.write(data)
            }
        });
        client.on('end', () => {
            console.log('disconnected from server');
        });
    }
    _c = c
    c.on('data', async (e) => {
        if (functionType == "listen") {
            logger.log('client', e.toString('hex'));
            console.log(e);
            console.log('client', e.byteLength);
            await sleep(delayTime)
            await client.write(e)
        } else if (functionType == "testServer") {

        } else if (functionType == "testClient") {
            logger.log('client', e.toString('hex'));
            // console.log(e);
            // console.log('client', e.byteLength);
            // a = Buffer.from([1,2,3])
            temBuf.push(...e)
            if(Buffer.from(temBuf).toString('hex').match(stateRegex)){
                var stateMatch = Buffer.from(temBuf).toString('hex').match(stateRegex)
                var stateLen = stateMatch[0].length
                var keyForCrypt = parseInt('0x'+stateMatch[1])
                var stateData = stateMatch[2]
                var stateDataCrc = stateMatch[3]
                temBuf.splice(0,stateMatch.index + stateLen)
                var stateDataStr = Buffer.from(stateData,'hex').map(e=>keyCrypt(keyForCrypt,e)).toString('hex')
                console.log(getState(stateDataStr))
                fs.writeFile("currentState.txt", stateDataStr, function (err) {
                    if (err) return console.log(err);
                });

            }else if(temBuf.length>2048){
                temBuf.length = 0
            }
            await sleep(delayTime)
            await client.write(e)
        } else if (functionType == "testClientLimitTimes") {
            if (limitTimes < limitMaxTimes) {
                logger.log('client', e.toString('hex'));
                console.log(e);
                console.log('client', e.byteLength);
                await sleep(delayTime)
                await client.write(e)
                limitTimes++
            }
        }

    });
    c.on('end', () => {
        console.log('client disconnected');
    });
    c.on('error', () => {
        console.log('client error');
    });
    c.on("close",()=>{
        console.log('client close');
    })
});
server.on('error', (err) => {
    throw err;
});
server.listen(6500, () => {
    console.log('server bound');
});


