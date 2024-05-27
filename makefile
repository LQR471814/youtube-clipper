NPM = pnpm
NPX = pnpm exec
PROTO = $(wildcard proto/*.proto)

ifeq ($(OS),Windows_NT)
	EXT = .exe
endif

TARGET_TRIPLE = $(shell rustc -vV | sed -n 's|host: ||p')

server-bin:
	cd server && pyinstaller main.py -F -n server-$(TARGET_TRIPLE)$(EXT)
