% Лабораторная работа № 1.1. Раскрутка самоприменимого компилятора
% 16 февраля 2026 г.
% Дмитрий Трофименко, ИУ9-62Б

# Цель работы
Целью данной работы является ознакомление с раскруткой самоприменимых компиляторов на примере модельного компилятора.

# Индивидуальный вариант
Компилятор P5. Добавить в язык двоичные константы вида 0b10010.


# Реализация

Различие между файлами `pcom.pas` и `pcom2.pas`:

```diff
--- pcom.pas    2026-02-15 23:17:28.718308100 +0300
+++ pcom2.pas   2026-02-15 23:23:37.789634600 +0300
@@ -1364,6 +1364,34 @@
         begin op := noop; i := 0;
           repeat i := i+1; if i<= digmax then digit[i] := ch; nextch
           until chartp[ch] <> number;
+          { Binary integer constants: 0b1010 (case-insensitive 'b'). }
+          if (i = 1) and (digit[1] = '0') and (lcase(ch) = 'b') then
+            begin
+              nextch; { consume 'b' }
+              with val do
+                begin
+                  ival := 0;
+                  if not (ch in ['0','1']) then error(201);
+                  while chartp[ch] = number do
+                    begin
+                      if (ch = '0') or (ch = '1') then
+                        begin
+                          if ival <= (maxint div 2) then
+                            ival := ival*2 + ordint[ch]
+                          else begin error(203); ival := 0 end
+                        end
+                      else
+                        begin
+                          { invalid digit in binary constant }
+                          error(203)
+                        end;
+                      nextch
+                    end;
+                  sy := intconst; op := noop
+                end
+            end
+          else
+
           if ((ch = '.') and (input^ <> '.') and (input^ <> ')')) or
              (lcase(ch) = 'e') then
             begin
```

Различие между файлами `pcom2.pas` и `pcom3.pas`:

```diff
--- pcom2.pas   2026-02-15 23:23:37.789634600 +0300
+++ pcom3.pas   2026-02-15 23:36:26.351500000 +0300
@@ -245,8 +245,8 @@

    This configuration is for a 32 bit machine as follows:

-   integer               32  bits
-   real                  64  bits
+   integer               0b100000  bits
+   real                  0b1000000  bits
    char                  8   bits
    boolean               8   bits
    set                   256 bits
```

# Тестирование

Тестовый пример:

```pascal
program hello(output);

var
  x: integer;

begin
  x := 0b10010;
  writeln('x=',x);
end.
```

Вывод тестового примера на `stdout`

```
x=         18
```

# Вывод

