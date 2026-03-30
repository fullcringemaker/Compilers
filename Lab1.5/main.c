#include <stdio.h>
#include <stdlib.h>
#include "scanner.h"

extern FILE *yyin;
int yylex(YYSTYPE *yylval, YYLTYPE *yylloc);

int main(void)
{
    const char *name = "input.txt";
    FILE *f = fopen(name, "r");
    YYSTYPE value;
    YYLTYPE coords;
    int tag;

    if (f == NULL)
    {
        printf("Cannot open file %s\n", name);
        return 1;
    }

    yyin = f;
    init_scanner();

    printf("TOKENS\n");
    do
    {
        tag = yylex(&value, &coords);
        if (tag != 0)
            print_token(tag, &value, &coords);
    }
    while (tag != 0);
    printf("\n");

    printf("IDENTIFIER TABLE\n");
    print_name_table();
    printf("\n");

    printf("ERRORS\n");
    print_errors();
    printf("\n");

    fclose(f);

    free_errors();
    free_names();
    destroy_scanner();

    return 0;
}
