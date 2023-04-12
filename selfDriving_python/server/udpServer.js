import dgram from 'node:dgram';
const { Console } = require('console');
const output = fs.createWriteStream('./stdout.log', {flags:'a'});
const errorOutput = fs.createWriteStream('./stderr.log', {flags:'a'});
const logger = new Console({ stdout: output, stderr: errorOutput });

var server = dgram.createSocket('udp4');

server.on('error', (err) => {
  console.error(`server error:\n${err.stack}`);
  server.close();
});

server.on('message', (msg, rinfo) => {
  ip = rinfo.address
  port = rinfo.port
  f =rinfo
  logger.log(msg.toString())
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

// import dgram from 'node:dgram';
// import { Buffer } from 'node:buffer';

// var message = Buffer.from("print('abc\r\n')");
// var client = dgram.createSocket('udp4');
// client.send(message, 1000,'192.168.2.106', (err) => {console.log(err)});

// client.on('message',(msg, rinfo) => {
//   console.log(`client got: ${msg} from ${rinfo.address}:${rinfo.port}`);
// });
