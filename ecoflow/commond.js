const comandList = {
    turn_on_12v: Buffer.from("aa020100a00d00000000000020022025012976", "hex"),
    turn_off_12v: Buffer.from("aa020100a00d0000000000002002202500e8b6", "hex"),
    turn_on_5v: Buffer.from("aa020100a00d00000000000020022022012b46", "hex"),
    turn_off_5v: Buffer.from("aa020100a00d0000000000002002202200ea86", "hex"),
    turn_on_220v: Buffer.from("aa020700de0d0000000000002004204201ffffffffffff3e28", "hex"),
    turn_off_220v: Buffer.from("aa020700de0d0000000000002004204200ffffffffffff2ee8", "hex"),
}

// aa02 01 00 a00d 0000 0000000020022025 01 2976
// aa02 00 00 b50d 0000 0000000020020141 62e0
// aa02 00 00 b50d 0000 00000000200b0141 b2e2
// aa02 01 00 a00d 0000 0000000020022022 01 2b46
// aa02 00 00 b50d 0000 0000000020022002 3b41
// aa02 06 00 cb2c 2000 0000020104202020 6f2020242020 7d3c
// aa02 06 00 cb2c 2100 0000020104202020 742121252121 12eb
// aa02 06 00 cb2c 2600 0000020104202020 762626222626 17bc
// aa02 06 00 cb2c 2700 0000020104202020 712727232727 7a37
// aa02 07 00 de0d 0000 0000000020042042 00ffffffffffff 2ee8
// aa02 6f 00 832f 1c00 0000ffff02202002 1c1c1c1c1c1f1e1d1d1c1c1c1c1c161b1c1c1c7a1c1c1c1d1d1b1c1c1c1c1c1c1c1c1c3d021c161c780f1c1c1c47d81c1cc5051c1cdd0b1c1c747b1c1c487a2b1c1c1c1c1cd2a41f1cb72a1d1c629d3e1c6e0c1c1c77fa761c1c1c1c1c1c1c1c1c1c1c1c949c1c1c141c1c1c1c1c1c cf8a

const serverReq = {
    ID: Buffer.from("aa020000b50d0000000000002002014162e0", "hex"),
    test1: Buffer.from("aa020000b50d000000000000200b0141b2e2", "hex"),
    state: Buffer.from("aa020000b50d000000000000200220023b41", "hex"),
    test3: Buffer.from("aa020000b50d0000000000002002010562d3", "hex"),
    test4: Buffer.from("aa020000b50d000000000000200320026a81", "hex"),
    test5: Buffer.from("aa020000b50d000000000000200301053313", "hex"),
    test6: Buffer.from("aa020000b50d00000000000020042002db40", "hex"),
    test7: Buffer.from("aa020000b50d0000000000002004010582d2", "hex"),
}


const keyValueTable = [
    [0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7, 0x8, 0x9, 0xa, 0xb, 0xc, 0xd, 0xe, 0xf],
    [0x1, 0x0, 0x3, 0x2, 0x5, 0x4, 0x7, 0x6, 0x9, 0x8, 0xb, 0xa, 0xd, 0xc, 0xf, 0xe],
    [0x2, 0x3, 0x0, 0x1, 0x6, 0x7, 0x4, 0x5, 0xa, 0xb, 0x8, 0x9, 0xe, 0xf, 0xc, 0xd],
    [0x3, 0x2, 0x1, 0x0, 0x7, 0x6, 0x5, 0x4, 0xb, 0xa, 0x9, 0x8, 0xf, 0xe, 0xd, 0xc],
    [0x4, 0x5, 0x6, 0x7, 0x0, 0x1, 0x2, 0x3, 0xc, 0xd, 0xe, 0xf, 0x8, 0x9, 0xa, 0xb],
    [0x5, 0x4, 0x7, 0x6, 0x1, 0x0, 0x3, 0x2, 0xd, 0xc, 0xf, 0xe, 0x9, 0x8, 0xb, 0xa],
    [0x6, 0x7, 0x4, 0x5, 0x2, 0x3, 0x0, 0x1, 0xe, 0xf, 0xc, 0xd, 0xa, 0xb, 0x8, 0x9],
    [0x7, 0x6, 0x5, 0x4, 0x3, 0x2, 0x1, 0x0, 0xf, 0xe, 0xd, 0xc, 0xb, 0xa, 0x9, 0x8],
    [0x8, 0x9, 0xa, 0xb, 0xc, 0xd, 0xe, 0xf, 0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7],
    [0x9, 0x8, 0xb, 0xa, 0xd, 0xc, 0xf, 0xe, 0x1, 0x0, 0x3, 0x2, 0x5, 0x4, 0x7, 0x6],
    [0xa, 0xb, 0x8, 0x9, 0xe, 0xf, 0xc, 0xd, 0x2, 0x3, 0x0, 0x1, 0x6, 0x7, 0x4, 0x5],
    [0xb, 0xa, 0x9, 0x8, 0xf, 0xe, 0xd, 0xc, 0x3, 0x2, 0x1, 0x0, 0x7, 0x6, 0x5, 0x4],
    [0xc, 0xd, 0xe, 0xf, 0x8, 0x9, 0xa, 0xb, 0x4, 0x5, 0x6, 0x7, 0x0, 0x1, 0x2, 0x3],
    [0xd, 0xc, 0xf, 0xe, 0x9, 0x8, 0xb, 0xa, 0x5, 0x4, 0x7, 0x6, 0x1, 0x0, 0x3, 0x2],
    [0xe, 0xf, 0xc, 0xd, 0xa, 0xb, 0x8, 0x9, 0x6, 0x7, 0x4, 0x5, 0x2, 0x3, 0x0, 0x1],
    [0xf, 0xe, 0xd, 0xc, 0xb, 0xa, 0x9, 0x8, 0x7, 0x6, 0x5, 0x4, 0x3, 0x2, 0x1, 0x0]
]

const keyCrypt = (key, value) => {
    var value_lsb = value & 0xf
    var value_msb = value >> 4
    var key_lsb = key & 0xf
    var key_msb = key >> 4
    return keyValueTable[key_lsb][value_lsb] + (keyValueTable[key_msb][value_msb] << 4)
}

const clientConfig = '3706000011000100524243425a355a443932373030363700695d53375759571954483841'
const stateConfig = {
    battery_volume:   14,
    _out_power:       15,
    _220v_input_power:17,
    _5v_on_off:       24, //0x18
    usb_power:        25,
    _12v_on_off:      33, //0x21
    temperature1:     35,
    temperature2:     36,
    wireless_power:   96,
    _220v_on_off:     99, //0x14
}

const getState = (dataStr) => {
    // var dataStrWithCrc = s.split('0000ffff02202002')[1]
    // var dataStr = dataStrWithCrc.substring(0,dataStrWithCrc.length-4)
    var state = Buffer.from(dataStr, 'hex')
    var _220v_on_off = state[stateConfig._220v_on_off] != 0
    var _5v_on_off = state[stateConfig._5v_on_off] != 0
    var _12v_on_off = state[stateConfig._12v_on_off] != 0
    var usb_power = state[stateConfig.usb_power] + 'w'
    var _out_power = state[stateConfig._out_power] + 'w'
    var _220v_input_power = state[stateConfig._220v_input_power] + 'w'
    var wireless_power = state[stateConfig.wireless_power] + 'w'
    var battery_volume = state[stateConfig.battery_volume] + '%'
    var temperature = (state[stateConfig.temperature1] + state[stateConfig.temperature2])/2 + '℃'
    return {
        // _5v_on_off,
        // _12v_on_off,
        // _220v_on_off,
        usb_power,
        _out_power,
        _220v_input_power,
        // wireless_power,
        battery_volume,
        temperature
    }
}

module.exports = {
    comandList, serverReq, keyCrypt, getState
}


// var fs = require('fs')
// var fileData
// fs.readFile('test.txt', (err, data) => {

//     var ss =data.toString()
//     fs.writeFile("state.txt", JSON.stringify(ss.trim().split('\n').map(s => {
        // var dataStrWithCrc = s.split('0000ffff02202002')[1]
        // var dataStr = dataStrWithCrc.substring(0, dataStrWithCrc.length - 4)
        // // return 
        // Buffer.from(dataStr, 'hex').map(e => keyCrypt(parseInt('0x' + s[12] + s[13]), e)).toString('hex')
//     })), function (err) {
//         if (err) return console.log(err);
//     });
    

// });

