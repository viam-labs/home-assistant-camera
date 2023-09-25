build:
	tar -czf module.tar.gz *.sh requirements.txt src

upload:
	viam module upload --version $(version) --platform linux/arm64 module.tar.gz
	viam module upload --version $(version) --platform linux/amd64 module.tar.gz
	viam module upload --version $(version) --platform darwin/arm64 module.tar.gz
	viam module upload --version $(version) --platform darwin/amd64 module.tar.gz

clean:
	rm module.tar.gz
