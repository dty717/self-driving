// import dgram from 'node:dgram';
const fs = require('fs');
const dgram = require('dgram');
const { Console } = require('console');
const output = fs.createWriteStream('./stdout.log', {flags:'a'});
const errorOutput = fs.createWriteStream('./stderr.log', {flags:'a'});
const logger = new Console({ stdout: output, stderr: errorOutput });

var isRecording = false;
var recordingStr = "";
var lastRecording = false;
var lastRecordingLength = 0;

var dataLen = 1200
var lastDataFrame = 1192

var flieLocation = 'C:/Users/18751/Desktop/github/dty717/self-driving/selfDriving_python/file/'

function createFile(data) {
  data = 'a=`' + data + '`'
  var dateStr = new Date().toISOString().replace(/T/, ' ').replace(/\..+/, '').replace(/[-\s:]/g, '_')
  fs.writeFile(flieLocation + dateStr + '.js', data, (err) => {
    if (err) throw err;
    console.log('The file has been saved!');
  });
}

var server = dgram.createSocket('udp4');

server.on('error', (err) => {
  console.error(`server error:\n${err.stack}`);
  server.close();
});

server.on('message', (msg, rinfo) => {
  ip = rinfo.address
  port = rinfo.port
  f =rinfo
  // logger.log(msg.toString())
  logger.log(new Date(new Date().getTime() + 1000 * 60 * 60 * 8), msg.toString())
  console.log(`server got: ${msg} from ${rinfo.address}:${rinfo.port}`);
  // server.send('hello world',rinfo.port,rinfo.address)
});

server.on('connect', () => {
  console.log('connect')
});
server.on('connection', () => {
  console.log('connection')
});
server.on('connecting', () => {
  console.log('connecting')
});
server.on('close', () => {
  console.log('close')
});
server.on('listening', () => {
  const address = server.address();
  console.log(`server listening ${address.address}:${address.port}`);
});

server.bind(41234);

// server.send('abc',53463, '104.238.132.153')
// server.send('[|gps forever|]',port, ip)
// server.send('[|update|]:lib/measure.py',port, ip)

// import dgram from 'node:dgram';
// import { Buffer } from 'node:buffer';

// var message = Buffer.from("print('abc\r\n')");
// var client = dgram.createSocket('udp4');
// client.send(message, 41234,'155.138.195.23', (err) => {console.log(err)});

// client.on('message',(msg, rinfo) => {
//   console.log(`client got: ${msg} from ${rinfo.address}:${rinfo.port}`);
// });
