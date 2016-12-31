REM @ECHO OFF

CALL make html
CALL make latex
cd build\latex
pdflatex MOUSE.tex
pdflatex MOUSE.tex
cd ..\..
COPY "build\latex\MOUSE.pdf" "..\Manual.pdf"