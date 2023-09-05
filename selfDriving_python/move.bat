mpy-cross.static-x64-windows-7.3.1.exe mainCode.py -o mainCode.mpy
mpy-cross.static-x64-windows-7.3.1.exe ov7670.py -o lib/ov7670.mpy
mpy-cross.static-x64-windows-7.3.1.exe pioasm_rxuart.py -o lib/pioasm_rxuart.mpy
mpy-cross.static-x64-windows-7.3.1.exe sim800_uart.py -o lib/sim800_uart.mpy
mpy-cross.static-x64-windows-7.3.1.exe logger.py -o lib/logger.mpy
mpy-cross.static-x64-windows-7.3.1.exe command.py -o lib/command.mpy
mpy-cross.static-x64-windows-7.3.1.exe measure.py -o lib/measure.mpy
set filePath=D:
@REM copy logger.py %filePath%\lib
@REM copy command.py %filePath%\lib
@REM copy sim800_uart.py %filePath%\lib
@REM copy ov7670.py %filePath%\lib
@REM copy pioasm_rxuart.py %filePath%\lib
@REM copy test.py %filePath%\lib
@REM copy code1.py %filePath%\code.py
@REM copy boot.py %filePath%

