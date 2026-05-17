% Лабораторная работа № 3.1 «Самоприменимый генератор компиляторов
  на основе предсказывающего анализа»

% Дмитрий Трофименко, ИУ9-62Б

# Цель работы
Целью данной работы является изучение алгоритма построения таблиц предсказывающего анализатора.

# Индивидуальный вариант
```
tokens (plus sign), (star), (n).
tokens (left paren), (right paren).
(E)   is (T) (E 1).
(E 1) is (plus sign) (T) (E 1),
(E 1) is .
(T)   is (F) (T 1).
(T 1) is (star) (F) (T 1),
(T 1) is .
(F)   is (n),
(F)   is (left paren) (E) (right paren).
(* аксиома *)
start (E).
```

# Грамматика на входном языке

```
GrammarDescription ::= TokensSection RulesSection StartSection
TokensSection ::= TokensDecl TokensSection | ε
TokensDecl ::= tokens SymbolList .
SymbolList ::= Symbol SymbolListTail
SymbolListTail ::= , Symbol SymbolListTail | ε
RulesSection ::= Rule RulesSection | ε
Rule ::= Symbol is RightPart RuleEnd
RightPart ::= SymbolSequence | ε
SymbolSequence ::= Symbol SymbolSequenceTail
SymbolSequenceTail ::= Symbol SymbolSequenceTail | ε
RuleEnd ::= . | ,
StartSection ::= start Symbol .
Symbol ::= ( Name )
Name ::= NamePart NameTail
NameTail ::= NamePart NameTail | ε
NamePart ::= IDENT | NUMBER
```

# Реализация
## Генератор компиляторов

```
…
```

## Калькулятор

```
…
```

# Тестирование
## Генератор компиляторов

Таблица для калькулятора

```
…
```

Таблица для собственной грамматики

```
…
```

## Калькулятор

…

# Вывод
…пишете, чему научились…
