# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.provision :shell, :path => "etc/bootstrap.sh"
  config.ssh.username = 'vagrant'
  config.vm.define "grumman" do |grumman|
    grumman.vm.box = "grumman"
    grumman.vm.host_name = "grumman"
  end
  config.vm.define "roger" do |roger|
    roger.vm.box = "roger"
    roger.vm.network :private_network, ip: "192.168.33.10"
    roger.vm.network "forwarded_port", guest: 80, host:8081
    roger.vm.network "forwarded_port", guest: 8080, host:8082
    roger.vm.host_name = 'roger'
  end
  config.vm.provider :digital_ocean do |provider, override|
    override.vm.box = 'grumman'
    override.ssh.private_key_path = '~/.ssh/id_rsa'
    provider.region = 'San Francisco 1'
    provider.setup = true
    provider.username = 'vagrant'
    provider.ca_path = "/etc/ssl/certs/ca-certificates.crt"
  end
end
