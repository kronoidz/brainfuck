STRING ENCODER by pekoo
This program receives a string and outputs a Brainfuck program that memorizes
the string in memory


Memorize input string from byte 1
>,[>,]
Rewind to beginning of string
<[<]>


[
    Memorize plus sign (43) on previous byte
    <+++++++++++++++++++++++++++++++++++++++++++ 43

    Output plus signs
    >[
        <.
        >-
    ]

    Output right arrow
    <+++++++++++++++++++ 19 .

    Output new line
    ---------------------------------------------------- 52 .
    >>
]
