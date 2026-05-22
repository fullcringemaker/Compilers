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
