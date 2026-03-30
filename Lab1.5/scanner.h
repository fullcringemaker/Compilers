#ifndef SCANNER_H
#define SCANNER_H

#include <stdio.h>

#define TAG_IDENT 1
#define TAG_NUMBER 2
#define TAG_PARENS 3
#define TAG_COLON 4
#define TAG_ASSIGN 5

extern char *tag_names[];

struct Position
{
    int line, pos, index;
};

void print_pos(struct Position *p);

struct Fragment
{
    struct Position starting, following;
};

typedef struct Fragment YYLTYPE;

void print_frag(struct Fragment *f);

union Token
{
    int ident_code;
    long long int num;
};

typedef union Token YYSTYPE;

void init_scanner(void);
void destroy_scanner(void);
void free_errors(void);
void free_names(void);
int add_name(const char *name);
void print_token(int tag, YYSTYPE *value, YYLTYPE *coords);
void print_name_table(void);
void print_errors(void);

#endif
