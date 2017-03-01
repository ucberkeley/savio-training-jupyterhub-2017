all: parallel.html parallel_slides.html

parallel.html: parallel.md
	pandoc -s -o parallel.html parallel.md

parallel_slides.html: parallel.md
	pandoc -s --webtex -t slidy -o parallel_slides.html parallel.md

clean:
	rm -rf parallel.html
