% Лабораторная работа 3.2 «Форматтер исходных текстов»
% 28 мая 2026 г.
% Дмитрий Трофименко, ИУ9-62Б

# Цель работы
Целью данной работы является приобретение навыков использования генератора синтаксических анализаторов 
bison.

# Индивидуальный вариант
```
Статически типизированный функциональный язык программирования:

-- Объединение двух списков
zip(xs : [int], ys : [int]) : [(int, int)] =
  if null(xs) or null(ys) then
    []
  else
    cons((car(xs), car(ys)), zip(cdr(xs), cdr(ys)));

-- Декартово произведение
cart_prod(xs : [int], ys : [int]) : [(int, int)] =
  if null(xs) then
    []
  else
    append(bind(car(xs), ys), cart_prod(cdr(xs), ys));

bind(x : int, ys : [int]) : [(int, int)] =
  if null(ys) then
    []
  else
    cons((x, car(ys)), bind(x, cdr(xs)));

-- Конкатенация списков пар
append(xs : [(int, int)], ys : [(int, int)]) : [(int, int)] =
  if null(xs) then
    ys
  else
    cons(car(xs), append(cdr(xs), ys));

-- Расплющивание вложенного списка
flat(xss : [[int]]) : [int] =
  if null(xss) then
    []
  else
    append(car(xss), flat(cdr(xss)));

-- Сумма элементов списка
sum(xs : [int]) : int =
  if null(xs) then
    0
  else
   car(xs) + sum(cdr(xs));

-- Вычисление полинома по схеме Горнера
polynom(x : int, coefs : [int]) : int =
  if null(coefs) then
    0
  else
    polynom(x, cdr(coefs)) * x + car(coefs);

-- Вычисление полинома x³+x²+x+1
polynom1111(x : int) : int = polynom(x, [1, 1, 1, 1]);

Сильный форматтер должен после then и перед else вставлять перевод строки.
```

# Реализация

lexer.h
```
#ifndef LEXER_H
#define LEXER_H

#include <stdio.h>

#ifndef YY_TYPEDEF_YY_SCANNER_T
#define YY_TYPEDEF_YY_SCANNER_T
typedef void *yyscan_t;
#endif

struct Extra {
    int cur_line;
    int cur_column;
};

void init_scanner(FILE *input, yyscan_t *scanner, struct Extra *extra);
void destroy_scanner(yyscan_t scanner);

#endif
```

lexer.l
```
%option reentrant noyywrap bison-bridge bison-locations
%option extra-type="struct Extra *"
%option noinput nounput

%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "lexer.h"
#include "parser.tab.h"

static char *copy_text(const char *text);

#define YY_USER_ACTION                                                   \
    do {                                                                 \
        int i;                                                           \
        struct Extra *extra = yyextra;                                   \
        yylloc->first_line = extra->cur_line;                            \
        yylloc->first_column = extra->cur_column;                        \
        for (i = 0; i < yyleng; ++i) {                                   \
            if (yytext[i] == '\n') {                                     \
                extra->cur_line += 1;                                    \
                extra->cur_column = 1;                                   \
            } else {                                                     \
                extra->cur_column += 1;                                  \
            }                                                            \
        }                                                                \
        yylloc->last_line = extra->cur_line;                             \
        yylloc->last_column = extra->cur_column;                         \
    } while (0);
%}

%%

[ \t\r\n]+              ;
"--"[^\n]*              ;

"if"                    return KW_IF;
"then"                  return KW_THEN;
"else"                  return KW_ELSE;
"or"                    return KW_OR;
"and"                   return KW_AND;
"int"                   return KW_INT;

[0-9]+                  {
                            yylval->text = copy_text(yytext);
                            return NUMBER;
                        }

[A-Za-z_][A-Za-z0-9_]*  {
                            yylval->text = copy_text(yytext);
                            return IDENT;
                        }

"("                     return '(';
")"                     return ')';
"["                     return '[';
"]"                     return ']';
","                     return ',';
":"                     return ':';
";"                     return ';';
"="                     return '=';
"+"                     return '+';
"-"                     return '-';
"*"                     return '*';
"/"                     return '/';

.                       return YYUNDEF;

%%

static char *copy_text(const char *text) {
    size_t length = strlen(text);
    char *result = (char *)malloc(length + 1);
    if (result == NULL) {
        fprintf(stderr, "not enough memory\n");
        exit(1);
    }
    memcpy(result, text, length + 1);
    return result;
}

void init_scanner(FILE *input, yyscan_t *scanner, struct Extra *extra) {
    extra->cur_line = 1;
    extra->cur_column = 1;

    if (yylex_init_extra(extra, scanner) != 0) {
        fprintf(stderr, "cannot initialize scanner\n");
        exit(1);
    }

    yyset_in(input, *scanner);
}

void destroy_scanner(yyscan_t scanner) {
    yylex_destroy(scanner);
}
```

parser.y
```
%code requires {
#include <stdio.h>
#include "lexer.h"

typedef struct FormatterContext FormatterContext;
}

%{
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct FormatterContext {
    FILE *output;
    int had_error;
};

static char *make_empty(void);
static char *make_text(const char *text);
static char *make_format(const char *format, ...);
static char *make_join(const char *left, const char *separator, const char *right);
static char *make_indent(const char *text, int spaces);
static char *make_if_expression(const char *condition,
                                const char *then_branch,
                                const char *else_branch);
static void free_if_not_null(char *text);
%}

%define api.pure full
%locations
%start program

%lex-param { yyscan_t scanner }
%parse-param { yyscan_t scanner }
%parse-param { FormatterContext *context }

%union {
    char *text;
}

%token KW_IF
%token KW_THEN
%token KW_ELSE
%token KW_OR
%token KW_AND
%token KW_INT
%token <text> IDENT
%token <text> NUMBER

%type <text> program
%type <text> definition
%type <text> optional_parameters
%type <text> parameter_list
%type <text> parameter
%type <text> type
%type <text> expression
%type <text> logic_expression
%type <text> additive_expression
%type <text> multiplicative_expression
%type <text> unary_expression
%type <text> primary_expression
%type <text> optional_arguments
%type <text> argument_list

%code provides {
int yylex(YYSTYPE *yylval_param, YYLTYPE *yylloc_param, yyscan_t scanner);
void yyerror(YYLTYPE *location,
             yyscan_t scanner,
             FormatterContext *context,
             const char *message);
}

%%

program:
      %empty
      {
          $$ = make_empty();
      }
    | program definition
      {
          free_if_not_null($1);
          free_if_not_null($2);
          $$ = make_empty();
      }
    ;

definition:
      IDENT '(' optional_parameters ')' ':' type '=' expression ';'
      {
          if (strchr($8, '\n') != NULL) {
              char *body = make_indent($8, 2);
              fprintf(context->output,
                      "%s(%s) : %s =\n%s;\n\n",
                      $1,
                      $3,
                      $6,
                      body);
              free_if_not_null(body);
          } else {
              fprintf(context->output,
                      "%s(%s) : %s = %s;\n\n",
                      $1,
                      $3,
                      $6,
                      $8);
          }

          free_if_not_null($1);
          free_if_not_null($3);
          free_if_not_null($6);
          free_if_not_null($8);
          $$ = make_empty();
      }
    ;

optional_parameters:
      %empty
      {
          $$ = make_empty();
      }
    | parameter_list
      {
          $$ = $1;
      }
    ;

parameter_list:
      parameter
      {
          $$ = $1;
      }
    | parameter_list ',' parameter
      {
          $$ = make_join($1, ", ", $3);
          free_if_not_null($1);
          free_if_not_null($3);
      }
    ;

parameter:
      IDENT ':' type
      {
          $$ = make_format("%s : %s", $1, $3);
          free_if_not_null($1);
          free_if_not_null($3);
      }
    ;

type:
      KW_INT
      {
          $$ = make_text("int");
      }
    | '[' type ']'
      {
          $$ = make_format("[%s]", $2);
          free_if_not_null($2);
      }
    | '(' type ',' type ')'
      {
          $$ = make_format("(%s, %s)", $2, $4);
          free_if_not_null($2);
          free_if_not_null($4);
      }
    ;

expression:
      KW_IF expression KW_THEN expression KW_ELSE expression
      {
          $$ = make_if_expression($2, $4, $6);
          free_if_not_null($2);
          free_if_not_null($4);
          free_if_not_null($6);
      }
    | logic_expression
      {
          $$ = $1;
      }
    ;

logic_expression:
      additive_expression
      {
          $$ = $1;
      }
    | logic_expression KW_OR additive_expression
      {
          $$ = make_join($1, " or ", $3);
          free_if_not_null($1);
          free_if_not_null($3);
      }
    | logic_expression KW_AND additive_expression
      {
          $$ = make_join($1, " and ", $3);
          free_if_not_null($1);
          free_if_not_null($3);
      }
    ;

additive_expression:
      multiplicative_expression
      {
          $$ = $1;
      }
    | additive_expression '+' multiplicative_expression
      {
          $$ = make_join($1, " + ", $3);
          free_if_not_null($1);
          free_if_not_null($3);
      }
    | additive_expression '-' multiplicative_expression
      {
          $$ = make_join($1, " - ", $3);
          free_if_not_null($1);
          free_if_not_null($3);
      }
    ;

multiplicative_expression:
      unary_expression
      {
          $$ = $1;
      }
    | multiplicative_expression '*' unary_expression
      {
          $$ = make_join($1, " * ", $3);
          free_if_not_null($1);
          free_if_not_null($3);
      }
    | multiplicative_expression '/' unary_expression
      {
          $$ = make_join($1, " / ", $3);
          free_if_not_null($1);
          free_if_not_null($3);
      }
    ;

unary_expression:
      primary_expression
      {
          $$ = $1;
      }
    | '-' unary_expression
      {
          $$ = make_format("-%s", $2);
          free_if_not_null($2);
      }
    ;

primary_expression:
      IDENT
      {
          $$ = $1;
      }
    | NUMBER
      {
          $$ = $1;
      }
    | IDENT '(' optional_arguments ')'
      {
          $$ = make_format("%s(%s)", $1, $3);
          free_if_not_null($1);
          free_if_not_null($3);
      }
    | '[' optional_arguments ']'
      {
          $$ = make_format("[%s]", $2);
          free_if_not_null($2);
      }
    | '(' expression ')'
      {
          $$ = make_format("(%s)", $2);
          free_if_not_null($2);
      }
    | '(' expression ',' expression ')'
      {
          $$ = make_format("(%s, %s)", $2, $4);
          free_if_not_null($2);
          free_if_not_null($4);
      }
    ;

optional_arguments:
      %empty
      {
          $$ = make_empty();
      }
    | argument_list
      {
          $$ = $1;
      }
    ;

argument_list:
      expression
      {
          $$ = $1;
      }
    | argument_list ',' expression
      {
          $$ = make_join($1, ", ", $3);
          free_if_not_null($1);
          free_if_not_null($3);
      }
    ;

%%

static char *make_empty(void) {
    return make_text("");
}

static char *make_text(const char *text) {
    size_t length = strlen(text);
    char *result = (char *)malloc(length + 1);
    if (result == NULL) {
        fprintf(stderr, "not enough memory\n");
        exit(1);
    }
    memcpy(result, text, length + 1);
    return result;
}

static char *make_format(const char *format, ...) {
    va_list arguments;
    va_list copy;
    int length;
    char *result;

    va_start(arguments, format);
    va_copy(copy, arguments);
    length = vsnprintf(NULL, 0, format, copy);
    va_end(copy);

    if (length < 0) {
        fprintf(stderr, "formatting error\n");
        exit(1);
    }

    result = (char *)malloc((size_t)length + 1);
    if (result == NULL) {
        fprintf(stderr, "not enough memory\n");
        exit(1);
    }

    vsnprintf(result, (size_t)length + 1, format, arguments);
    va_end(arguments);
    return result;
}

static char *make_join(const char *left, const char *separator, const char *right) {
    return make_format("%s%s%s", left, separator, right);
}

static char *make_indent(const char *text, int spaces) {
    size_t text_length = strlen(text);
    size_t capacity = text_length + 1;
    size_t position = 0;
    char *result;
    int at_line_start = 1;
    size_t i;

    for (i = 0; i < text_length; ++i) {
        if (at_line_start && text[i] != '\n') {
            capacity += (size_t)spaces;
            at_line_start = 0;
        }
        if (text[i] == '\n') {
            at_line_start = 1;
        }
    }

    result = (char *)malloc(capacity);
    if (result == NULL) {
        fprintf(stderr, "not enough memory\n");
        exit(1);
    }

    at_line_start = 1;
    for (i = 0; i < text_length; ++i) {
        if (at_line_start && text[i] != '\n') {
            int j;
            for (j = 0; j < spaces; ++j) {
                result[position++] = ' ';
            }
            at_line_start = 0;
        }

        result[position++] = text[i];

        if (text[i] == '\n') {
            at_line_start = 1;
        }
    }

    result[position] = '\0';
    return result;
}

static char *make_if_expression(const char *condition,
                                const char *then_branch,
                                const char *else_branch) {
    char *formatted_then = make_indent(then_branch, 2);
    char *formatted_else = make_indent(else_branch, 2);
    char *result = make_format("if %s then\n%s\nelse\n%s",
                               condition,
                               formatted_then,
                               formatted_else);

    free_if_not_null(formatted_then);
    free_if_not_null(formatted_else);
    return result;
}

static void free_if_not_null(char *text) {
    if (text != NULL) {
        free(text);
    }
}

void yyerror(YYLTYPE *location,
             yyscan_t scanner,
             FormatterContext *context,
             const char *message) {
    (void)scanner;
    context->had_error = 1;
    fprintf(stderr,
            "syntax error at line %d, column %d: %s\n",
            location->first_line,
            location->first_column,
            message);
}

int main(int argc, char **argv) {
    FILE *input;
    FILE *output;
    yyscan_t scanner;
    struct Extra extra;
    FormatterContext context;
    int parse_result;

    if (argc < 3) {
        fprintf(stderr, "usage: %s <input.txt> <output.txt>\n", argv[0]);
        return 1;
    }

    input = fopen(argv[1], "r");
    if (input == NULL) {
        fprintf(stderr, "cannot open input file: %s\n", argv[1]);
        return 1;
    }

    output = fopen(argv[2], "w");
    if (output == NULL) {
        fprintf(stderr, "cannot open output file: %s\n", argv[2]);
        fclose(input);
        return 1;
    }

    context.output = output;
    context.had_error = 0;

    init_scanner(input, &scanner, &extra);
    parse_result = yyparse(scanner, &context);
    destroy_scanner(scanner);

    fclose(input);
    fclose(output);

    if (parse_result != 0 || context.had_error) {
        return 1;
    }

    return 0;
}
```


# Тестирование

Входные данные

```text
-- Объединение двух списков
zip(xs:[int],ys:[int]):[(int,int)]=if null(xs) or null(ys) then [] else cons((car(xs),car(ys)),zip
(cdr(xs),cdr(ys)));

-- Декартово произведение
cart_prod(xs:[int],ys:[int]):[(int,int)]=if null(xs) then [] else append(bind(car(xs),ys),cart_prod
(cdr(xs),ys));

bind(x:int,ys:[int]):[(int,int)]=if null(ys) then [] else cons((x,car(ys)),bind(x,cdr(xs)));

-- Конкатенация списков пар
append(xs:[(int,int)],ys:[(int,int)]):[(int,int)]=if null(xs) then ys else cons(car(xs),append
(cdr(xs),ys));

-- Расплющивание вложенного списка
flat(xss:[[int]]):[int]=if null(xss) then [] else append(car(xss),flat(cdr(xss)));

-- Сумма элементов списка
sum(xs:[int]):int=if null(xs) then 0 else car(xs)+sum(cdr(xs));

-- Вычисление полинома по схеме Горнера
polynom(x:int,coefs:[int]):int=if null(coefs) then 0 else polynom(x,cdr(coefs))*x+car(coefs);

-- Вычисление полинома x³+x²+x+1
polynom1111(x:int):int=polynom(x,[1,1,1,1]);
```

Вывод на `stdout`

```
zip(xs : [int], ys : [int]) : [(int, int)] =
  if null(xs) or null(ys) then
    []
  else
    cons((car(xs), car(ys)), zip(cdr(xs), cdr(ys)));

cart_prod(xs : [int], ys : [int]) : [(int, int)] =
  if null(xs) then
    []
  else
    append(bind(car(xs), ys), cart_prod(cdr(xs), ys));

bind(x : int, ys : [int]) : [(int, int)] =
  if null(ys) then
    []
  else
    cons((x, car(ys)), bind(x, cdr(xs)));

append(xs : [(int, int)], ys : [(int, int)]) : [(int, int)] =
  if null(xs) then
    ys
  else
    cons(car(xs), append(cdr(xs), ys));

flat(xss : [[int]]) : [int] =
  if null(xss) then
    []
  else
    append(car(xss), flat(cdr(xss)));

sum(xs : [int]) : int =
  if null(xs) then
    0
  else
    car(xs) + sum(cdr(xs));

polynom(x : int, coefs : [int]) : int =
  if null(coefs) then
    0
  else
    polynom(x, cdr(coefs)) * x + car(coefs);

polynom1111(x : int) : int = polynom(x, [1, 1, 1, 1]);
```

# Вывод
В данной лабораторной работе был разработан сильный форматтер исходных текстов, который принимает 
программу на входном языке, выполняет разбор её структуры и выводит эквивалентный текст в едином 
оформлении. По условию требовалось получать на выходе отформатированный исходный текст, соблюдающий 
выбранные правила записи и расстановки пробелов и переводов строк, а также завершать работу при первой 
синтаксической ошибке, чтобы результат оставался корректным для дальнейшего использования.

В ходе выполнения работы были последовательно реализованы этапы построения анализаторов и связки между 
ними, после чего в процесс разбора были добавлены действия, формирующие выходной текст по мере 
распознавания конструкций. Индивидуальный вариант задавал функциональный язык со статической типизацией 
и требовал отдельного правила оформления условных выражений, поэтому при порождении результата было 
обеспечено форматирование таких конструкций с обязательными переводами строк в заданных местах и с 
выравниванием вложенных частей по отступам.

Тестирование на наборе примеров показало, что форматтер стабильно преобразует слитно записанные 
фрагменты в читаемый вид, корректно расставляет пробелы, отступы и переносы строк в определениях и 
выражениях, а также выполняет специальное правило оформления условной конструкции. Итогом работы стал 
инструмент, который автоматически приводит программы к единому стилю
