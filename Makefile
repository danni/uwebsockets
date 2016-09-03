AMPY := ampy

SOURCES = \
	uwebsockets/client.py \
	uwebsockets/protocol.py \
	usocketio/client.py \
	usocketio/protocol.py \
	usocketio/transport.py \
	$(NULL)

__deploy__/%.py: %.py
	@mkdir -p $(dir $@)
	$(AMPY) put $< $<
	@cp $< $@

deploy: $(addprefix __deploy__/, $(SOURCES))
