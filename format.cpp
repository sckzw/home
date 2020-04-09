#include <iostream>

int main( void )
{
}

#define TEST         \
    "long long test" \
    "string"         \
    "!!"

class hoge
{
public: // <- access-label
    // :
    // :
    // :

protected: // <- access-label
    // :
    // :
    // :

private: // <- access-label
    // :
    // :
    // :
};

int hoge(
    int x, // <- arglist-intro
    int y, // <- arglist-cont
    int z  // <- arglist-cont
    )      // <- arglist-close
{
    // :
    // :
    // :
}

int fuga( int x,
          int y,  // <- arglist-cont-nonempty
          int z ) // <- arglist-cont-nonempty
{
    // :
    // :
    // :
}

hoge hoge_array [] =
{
    {
        // :
        // :
        // :
    },
    { // <- brace-entry-open
        // :
        // :
        // :
    },
    // :
    // :
    // :
};

hoge hoge_array [] =
{ // <- brace-list-open
    0, // <- brace-list-intro
    1, // <- brace-list-entry
    2, // <- brace-list-entry
}; // <- brace-list-close

/*
 * <- c
 */ // <- c

void test()
{
    switch ( c )
    {
    case 'a': // <- case-label
        foo;
        // :
        // :
        // :
        break;
    case 'b': // <- case-label
        bar;
        // :
        // :
        // :
        break;
    default: // <- case-label
        baz;
        // :
        // :
        // :
        break;
    };

    try
    {
        foo;
        // :
        // :
        // :
    }
    catch // <- catch-clause
        (
            // :
        )
    {
        bar;
        // :
        // :
        // :
    }
}

class hoge
{ // <- class-open
    // :
    // :
    // :
}; // <- class-close

// Comment <- comment-intro

/* Comment */ // <- comment-intro

/* <- comment-intro
 * Comment
 */

#include <cstdlib> // <- cpp-macro

void hoge()
{ // <- defun-open
    // <- defun-block-intro
    // :
    // :
    // :
} // <- defun-close

void test2( void )
{
    do
    {
        // :
        // :
        // :
    }
    while ( flag ); // <- do-while-closure

    if ( a == 0 )
    {
        // :
        // :
        // :
    }
    else // <- else-clause
    {
        // :
        // :
        // :
    }
}

extern "C"
{ // <- extern-lang-open
    // :
    // :
    // :
} // <- extern-lang-close

class hoge
{
    friend class fuga; // <- friend

    // :
    // :
    // :
};

void
hoge
(
)
    throw // <- func-decl-cont
    ( // <- func-decl-cont
    ) // <- func-decl-cont
{
    // :
    // :
    // :
}

void
fuga::piyo
(
)
    const // <- func-decl-cont
{
    // :
    // :
    // :
}

class hoge
{
public:
    hoge();  // <- inclass
    ~hoge(); // <- inclass
    // :
    // :
    // :
};

extern "C"
{
    // <- inextern-lang
    // :
    // :
    // :
}

class hoge: public fuga, // <- inher-intro
            public piyo // <- inher-cont
{
    // :
    // :
    // :
};

class hoge
{
public:
    hoge
    (
    )
    { // <- inline-open
        // :
        // :
        // :
    } // <- inline-close
};

namespace hoge
{
    // <- innamespace
    // :
    // :
    // :
}

hoge::hoge
(
):
    fuga ( 1 ), // <- member-init-intro
    piyo ( 2 ), // <- member-init-cont
    nyaa ( 3 ) // <- member-init-cont
{
    // :
    // :
    // :
}

namespace hoge
{ // <- namespace-open
    // :
    // :
    // :
} // <- namespace-close

void
hoge
(
)
{
    {
        // <- statement-block-intro
        // :
        // :
        // :
    }

    // :
    // :
    // :
    switch ( c )
    {
    case 'a':
        // <- statement-case-intro
        // :
        // :
        // :

    case 'b':
        { // <- statement-case-open
            // :
            // :
            // :
        }
    }

    hoge =
        fuga + piyo; // <- statement-cont

    std::cout
        << hoge
        << fuga       // <- stream-op
        << std::endl; // <- stream-op
}

void
hoge
(
)
{
    fuga = R"[I learned to understand Cezanne much better,
and to see truly how he made landscapes when I was hungry.]"; // <- string

    // :
    // :
    // :

    if ( a == 0 )
        hoge (); // <- substatement

    if ( b < 0 )
        b = -( b + 1 ); // <- substatement
    else
        b += 1; // <- substatement

    while ( c > 0 )
        --c; // <- substatement

    for ( std::size_t i = 0; i < N; ++i )
        std::cout << "i: " << i << std::endl; // <- substatement

    do
        fuga () // <- substatement
            while ( piyo () );

    if ( d == 0 )
    { // <- substatement-open
        // :
        // :
        // :
    }

    try
    { // <- substatement-open
        // :
        // :
        // :
    }
    catch
        (
            // :
        )
    { // <- substatement-open
        // :
        // :
        // :
    }
}

template
<
    class hoge, // <- template-args-cont
    class fuga // <- template-args-cont
    > // <- template-args-cont
void
hoge
(
)
{
    // :
    // :
    // :
}

void // <- topmost-intro
hoge // <- topmost-intro-cont
( // <- topmost-intro-cont
)
{
    // :
    // :
    // :
}

int main( int, char**, int );

int main( int argc, char** argv, int argv )
{
    sc_in< sc_uint< 8 > > dat;

    if ( argc == 1 )
        return 0;

    a = b + d + d;

    sample( arg1,
            arg2 );

    return 0;
}
