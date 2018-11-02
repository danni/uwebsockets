AMPY := ampy

DIRECTORIES = \
	uwebsockets \
  usocketio \
	$(NULL)

SOURCES = \
	uwebsockets/client.py \
	uwebsockets/protocol.py \
	usocketio/client.py \
	usocketio/protocol.py \
	usocketio/transport.py \
	$(NULL)

__mkdir__/% : %
	@mkdir -p $(dir $@)
	$(AMPY) mkdir $<
	@touch $@

__deploy__/%.py: %.py
	@mkdir -p $(dir $@)
	$(AMPY) put $< $<
	@cp $< $@

__remove_file__/%.py : %.py
	$(AMPY) rm $< || echo 'Already deleted'
	@rm -r __deploy__/$<

__remove_dir__/% : %
	$(AMPY) rmdir $< || echo 'Already deleted'
	@rm -r __mkdir__/$<
	@rm -r __deploy__/$<


deploy: $(addprefix __mkdir__/, $(DIRECTORIES)) $(addprefix __deploy__/, $(SOURCES))

.PHONY: clean
clean: $(addprefix __remove_dir__/, $(DIRECTORIES))
