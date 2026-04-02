asciidoctor -b docbook rogaikopyta.adoc -o tmp.xml && \
pandoc tmp.xml -f docbook -t docx -o tmp.docx --reference-doc=custom-reference.docx