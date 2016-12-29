@ECHO OFF
DEL OstModel*.txt >NUL 2>NUL
DEL runFileMPI* >NUL 2>NUL
DEL OstErrors*.txt >NUL 2>NUL
DEL OstTemp*.txt >NUL 2>NUL
DEL OstOutput*.txt >NUL 2>NUL
DEL OstStatus0.txt >NUL 2>NUL
DEL OstQuit.txt >NUL 2>NUL
DEL OstArchive.txt >NUL 2>NUL
DEL OstDDSPn.txt >NUL 2>NUL
DEL dds_status.out >NUL 2>NUL
DEL OstrichErrors.log >NUL 2>NUL
DEL Proc*.stdout >NUL 2>NUL
DEL *.Barrier.*.* >NUL 2>NUL
DEL *.dirlist.*.* >NUL 2>NUL
DEL *.Reduce.*.* >NUL 2>NUL
DEL *.Sync.*.* >NUL 2>NUL
DEL *.Broadcast.*.* >NUL 2>NUL
DEL MPI_Abort.txt >NUL 2>NUL
RMDIR /S /Q model0 >NUL 2>NUL
RMDIR /S /Q model1 >NUL 2>NUL
RMDIR /S /Q model2 >NUL 2>NUL
RMDIR /S /Q model3 >NUL 2>NUL
RMDIR /S /Q model4 >NUL 2>NUL
RMDIR /S /Q model5 >NUL 2>NUL
RMDIR /S /Q model6 >NUL 2>NUL
RMDIR /S /Q model7 >NUL 2>NUL