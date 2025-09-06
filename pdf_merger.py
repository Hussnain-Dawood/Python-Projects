import PyPDF2
# Create a PdfFileMerger object
merge=PyPDF2.PdfFileMerger()
# List of pdf files to merge

pdffiles=['file1.pdf','file2.pdf'] # replace the name with you pdf files
# Loop through all pdf files
for filename in pdffiles:
    # Open each pdf file
    pdffile=open(filename,'rb')
    # Create a PdfFileReader object
    pdfreader=PyPDF2.PdfFileReader(pdffile)
    merge.append(pdfreader)
pdffile.close()
merge.write('merged.pdf')   