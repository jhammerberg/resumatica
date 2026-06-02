\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{classic}[Classic Resume Class]

\LoadClass[letterpaper,11pt]{article}

\RequirePackage{latexsym}
\RequirePackage[empty]{fullpage}
\RequirePackage[explicit]{titlesec}
\RequirePackage{marvosym}
\RequirePackage[usenames,dvipsnames]{color}
\RequirePackage{verbatim}
\RequirePackage{enumitem}
\RequirePackage{fancyhdr}
\RequirePackage[english]{babel}
\RequirePackage{tabularx}
\RequirePackage{geometry}
\RequirePackage{fontspec}

\newfontfamily{\mediumfont}{Roboto-Regular.ttf}[
    Path = ./templates/fonts/Roboto/
]

\setmainfont{Roboto-Light.ttf}[
    Path = ./templates/fonts/Roboto/,
    BoldFont = Roboto-Bold.ttf,
    ItalicFont = Roboto-Italic.ttf,
    BoldItalicFont = Roboto-BoldItalic.ttf
]

% Define a custom command to call JetBrains Mono for titles
\newfontfamily{\titlefont}{JetBrainsMono-Regular.ttf}[
    Path = ./templates/fonts/JetBrainsMono/,
    BoldFont = JetBrainsMono-Bold.ttf,
    ItalicFont = JetBrainsMono-Italic.ttf,
    BoldItalicFont = JetBrainsMono-BoldItalic.ttf
]

\geometry{left=0.5in, top=0.5in, right=0.5in, bottom=0.5in}

\pagestyle{fancy}
\fancyhf{} % clear all header and footer fields
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

% Adjust margins
\addtolength{\oddsidemargin}{-0.0in}
\addtolength{\evensidemargin}{-0.0in}
\addtolength{\textwidth}{0.0in}
\addtolength{\topmargin}{-0.0in}
\addtolength{\textheight}{0.0in}

\RequirePackage[normalem]{ulem}
\RequirePackage[
  unicode,
  pdfencoding=auto,
  colorlinks=true,
  urlcolor=blue,
  linkcolor=blue,
]{hyperref}
\RequirePackage{bookmark}

\newcommand{\classic@linkuline}[1]{{\color{blue}\uline{#1}}}

\pdfstringdefDisableCommands{%
  \let\classic@linkuline\@firstofone
  \let\uline\@firstofone
  \let\color\@firstofone
}

\AtBeginDocument{%
  \urlstyle{same}%
  \let\classic@url\url
  \renewcommand{\url}[1]{\classic@linkuline{\classic@url{#1}}}%
  \let\classic@href\href
  \renewcommand{\href}[2]{\classic@href{#1}{\classic@linkuline{#2}}}%
}

\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

\setlength{\fboxrule}{1.25pt}

% Sections formatting
\titleformat{\section}
  {\vspace{-4pt}\titlefont\bfseries\raggedright\large}
  {}
  {0em}
  {\fbox{\textbf{#1}}} % The #1 represents the section title text
  [\vspace{-1.1pt} \color{black}{\titlerule[1.25pt]} \vspace{-5pt}]

% Custom commands
\newcommand{\resumeItem}[1]{
  \item\small{
    {#1 \vspace{-2pt}}
  }
}

% Subheading formatting (Company/Location in JetBrains, Title/Date in Roboto Medium)
\newcommand{\resumeSubheading}[4]{
  \vspace{-2pt}\item
    \begin{tabular*}{0.97\textwidth}[t]{l@{\extracolsep{\fill}}r}
      {\titlefont\textbf{#1}} & {\titlefont\textbf{#2}} \\
      {\mediumfont\small #3} & {\mediumfont\small #4} \\
    \end{tabular*}\vspace{-7pt}
}

% SubSubheading formatting (Title/Date in Roboto Medium)
\newcommand{\resumeSubSubheading}[2]{
    \item
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      {\mediumfont\small #1} & {\mediumfont\small #2} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeSubItem}[1]{\resumeItem{#1}\vspace{-4pt}}

\renewcommand\labelitemii{$\vcenter{\hbox{\tiny$\bullet$}}$}

\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.15in, label={}]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\newcommand{\resumeItemListStart}{\begin{itemize}}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}