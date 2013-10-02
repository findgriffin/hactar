# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.provision :shell, :path => "etc/bootstrap.sh"
  config.ssh.username = 'vagrant'
  config.ssh.private_key_path = '~/.ssh/id_rsa'
  config.vm.define "grumman" do |grumman|
    grumman.vm.box = "grumman"
  end
  config.vm.define "roger" do |roger|
    roger.vm.box = "roger"
    roger.vm.network :private_network, ip: "192.168.33.10"
  end
  config.vm.provider :digital_ocean do |provider, override|
    override.vm.box = 'grumman'
    provider.region = 'San Francisco 1'
    provider.setup = true
    provider.username = 'vagrant'
    provider.ca_path = "/etc/ssl/certs/ca-certificates.crt"
  end
end
