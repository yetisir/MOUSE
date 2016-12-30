REM @ECHO OFF

CALL make html
CALL make latex
cd _build\latex
pdflatex MOUSE.tex
pdflatex MOUSE.tex
cd ..\..
COPY "_build\latex\MOUSE.pdf" "..\Manual.pdf"