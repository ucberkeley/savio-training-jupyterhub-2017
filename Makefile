all: jh-intro.html jh-intro_slides.html

jh-intro.html: jh-intro.md
	pandoc -s -o jh-intro.html jh-intro.md

jh-intro_slides.html: jh-intro.md
	pandoc -s --webtex -t slidy -o jh-intro_slides.html jh-intro.md

clean:
	rm -rf jh-intro.html
