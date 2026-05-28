% Лабораторная работа № 1.5 «Порождение лексического анализатора с помощью flex»
% 30 марта 2026 г.
% Дмитрий Трофименко, ИУ9-62Б

# Цель работы
Целью данной работы является изучение генератора лексических анализаторов flex.

# Индивидуальный вариант
- Идентификаторы: либо последовательности латинских букв, либо непустые последовательности десятичных 
цифр, ограниченные круглыми скобками.
- Числовые литералы: либо последовательности десятичных цифр, не начинающиеся с нуля, либо «0».
- Операции: «()», «:», «:=».

## Лексический домен для защиты
Шестнадцатеричные числа начинаются на решётку

# Реализация

```flex
%option noyywrap bison-bridge bison-locations

%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include "scanner.h"

char *tag_names[] =
{
    "END_OF_PROGRAM",
    "IDENT",
    "NUMBER",
    "PARENS",
    "COLON",
    "ASSIGN"
};

struct ErrorMessage
{
    struct Position pos;
    char *text;
};

struct ErrorList
{
    struct ErrorMessage *data;
    int size;
    int capacity;
};

struct NameEntry
{
    char *name;
};

struct NameTable
{
    struct NameEntry *data;
    int size;
    int capacity;
};

static struct ErrorList errors = { NULL, 0, 0 };
static struct NameTable names = { NULL, 0, 0 };

int continued;
struct Position cur;

static char *dup_string(const char *s)
{
    size_t n = strlen(s);
    char *copy = (char *)malloc(n + 1);
    if (copy == NULL)
    {
        fprintf(stderr, "memory allocation error\n");
        exit(1);
    }
    memcpy(copy, s, n + 1);
    return copy;
}

static void reserve_errors(void)
{
    if (errors.size >= errors.capacity)
    {
        int new_capacity = errors.capacity == 0 ? 8 : errors.capacity * 2;
        struct ErrorMessage *new_data =
            (struct ErrorMessage *)realloc(errors.data, new_capacity * sizeof(struct ErrorMessage));
        if (new_data == NULL)
        {
            fprintf(stderr, "memory allocation error\n");
            exit(1);
        }
        errors.data = new_data;
        errors.capacity = new_capacity;
    }
}

static void reserve_names(void)
{
    if (names.size >= names.capacity)
    {
        int new_capacity = names.capacity == 0 ? 8 : names.capacity * 2;
        struct NameEntry *new_data =
            (struct NameEntry *)realloc(names.data, new_capacity * sizeof(struct NameEntry));
        if (new_data == NULL)
        {
            fprintf(stderr, "memory allocation error\n");
            exit(1);
        }
        names.data = new_data;
        names.capacity = new_capacity;
    }
}

void print_pos(struct Position *p)
{
    printf("(%d, %d)", p->line, p->pos);
}

void print_frag(struct Fragment *f)
{
    print_pos(&(f->starting));
    printf("-");
    print_pos(&(f->following));
}

static void add_error_at(struct Position pos, const char *msg)
{
    reserve_errors();
    errors.data[errors.size].pos = pos;
    errors.data[errors.size].text = dup_string(msg);
    errors.size++;
}

int add_name(const char *name)
{
    int i;
    for (i = 0; i < names.size; i++)
    {
        if (strcmp(names.data[i].name, name) == 0)
            return i;
    }

    reserve_names();
    names.data[names.size].name = dup_string(name);
    names.size++;
    return names.size - 1;
}

void print_token(int tag, YYSTYPE *value, YYLTYPE *coords)
{
    printf("%s ", tag_names[tag]);
    print_frag(coords);
    printf(":");

    if (tag == TAG_IDENT)
        printf(" %d", value->ident_code);
    else if (tag == TAG_NUMBER)
        printf(" %lld", value->num);

    printf("\n");
}

void print_name_table(void)
{
    int i;
    for (i = 0; i < names.size; i++)
        printf("%d: %s\n", i, names.data[i].name);
}

void print_errors(void)
{
    int i;
    for (i = 0; i < errors.size; i++)
    {
        printf("Error ");
        print_pos(&(errors.data[i].pos));
        printf(": %s\n", errors.data[i].text);
    }
}

void init_scanner(void)
{
    continued = 0;
    cur.line = 1;
    cur.pos = 1;
    cur.index = 0;
}

void destroy_scanner(void)
{
}

void free_errors(void)
{
    int i;
    for (i = 0; i < errors.size; i++)
        free(errors.data[i].text);
    free(errors.data);
    errors.data = NULL;
    errors.size = 0;
    errors.capacity = 0;
}

void free_names(void)
{
    int i;
    for (i = 0; i < names.size; i++)
        free(names.data[i].name);
    free(names.data);
    names.data = NULL;
    names.size = 0;
    names.capacity = 0;
}

#define YY_USER_ACTION \
{ \
    int i; \
    if (!continued) \
        yylloc->starting = cur; \
    continued = 0; \
    for (i = 0; i < yyleng; i++) \
    { \
        if (yytext[i] == '\n') \
        { \
            cur.line++; \
            cur.pos = 1; \
        } \
        else \
            cur.pos++; \
        cur.index++; \
    } \
    yylloc->following = cur; \
}

// Шестнадцатеричные числа начинаются на решётку

%}

LETTER [A-Za-z]
DIGIT [0-9]
IDENT_ALPHA {LETTER}+
IDENT_PAREN \({DIGIT}+\)
NUMBER 0|[1-9]{DIGIT}*
BAD_NUMBER 0{DIGIT}+
WS [ \t\r\n]+
HEX \#[0-9A-Fa-f]+

%%

{WS}

":=" return TAG_ASSIGN;
"()" return TAG_PARENS;
":" return TAG_COLON;

{IDENT_PAREN} {
    yylval->ident_code = add_name(yytext);
    return TAG_IDENT;
}

{IDENT_ALPHA} {
    yylval->ident_code = add_name(yytext);
    return TAG_IDENT;
}

{BAD_NUMBER} {
    add_error_at(yylloc->starting, "number literal cannot start with zero");
}

{NUMBER} {
    char *endptr;
    errno = 0;
    yylval->num = strtoll(yytext, &endptr, 10);
    if (errno == ERANGE || *endptr != '\0')
    {
        add_error_at(yylloc->starting, "integer literal overflow");
        continue;
    }
    return TAG_NUMBER;
}

{HEX} {
        char *endptr;
    errno = 0;
    yylval->num = strtoll(yytext+1, &endptr, 16);
    if (errno == ERANGE || *endptr != '\0')
    {
        add_error_at(yylloc->starting, "integer literal overflow");
        continue;
    }
    return TAG_NUMBER;
}

. {
    add_error_at(yylloc->starting, "unexpected character");
}

<<EOF>> return 0;

%%
```

# Тестирование

Входные данные

```text
abc (123) 0 17 () : :=
xyz (007) 5 001 () :
(42) := test 9
abc  #12FE
```

Вывод на `stdout`

```shell
TOKENS
IDENT (1, 1)-(1, 4): 0
IDENT (1, 5)-(1, 10): 1
NUMBER (1, 11)-(1, 12): 0
NUMBER (1, 13)-(1, 15): 17
PARENS (1, 16)-(1, 18):
COLON (1, 19)-(1, 20):
ASSIGN (1, 21)-(1, 23):
IDENT (2, 1)-(2, 4): 2
IDENT (2, 5)-(2, 10): 3
NUMBER (2, 11)-(2, 12): 5
PARENS (2, 17)-(2, 19):
COLON (2, 20)-(2, 21):
IDENT (3, 1)-(3, 5): 4
ASSIGN (3, 6)-(3, 8):
IDENT (3, 9)-(3, 13): 5
NUMBER (3, 14)-(3, 15): 9
IDENT (4, 1)-(4, 4): 0

IDENTIFIER TABLE
0: abc
1: (123)
2: xyz
3: (007)
4: (42)
5: test

ERRORS
Error (2, 13): number literal cannot start with zero
```

# Вывод
В данной лабораторной работе был изучен подход к построению лексического анализатора с использованием 
генератора flex, который по набору описаний доменов автоматически порождает код распознавания. В 
соответствии с заданием анализатор читает входной текст из файла, выделяет последовательность лексем, 
вычисляет координаты начала и конца каждой лексемы и выводит их в заданном формате, чтобы результат 
можно было напрямую использовать на следующем этапе обработки программы.

В ходе выполнения работы были заданы правила распознавания доменов индивидуального варианта и домена 
для защиты, а также определены действия, выполняемые при нахождении каждой лексемы. Для лексем с 
атрибутами реализовано вычисление соответствующих значений, включая преобразование числовых 
представлений в машинный тип и помещение идентификаторов в таблицу имён, чтобы одинаковые записи не 
дублировались и могли ссылаться на один и тот же элемент таблицы. Для лексем без атрибутов обеспечена 
корректная выдача только тега и координат, а пробельные фрагменты исключаются из выходного потока.

Отдельно была реализована обработка ошибок с накоплением сообщений и восстановлением, позволяющая 
продолжать анализ после некорректных фрагментов входа. При встрече неподходящей последовательности 
символов или неверной формы литерала формируется сообщение с координатой, после чего анализатор 
продвигается дальше и пытается распознать следующие лексемы. Тестирование на наборе входных строк 
подтвердило корректное распознавание всех предусмотренных доменов, правильное заполнение таблицы 
идентификаторов и формирование списка ошибок.
