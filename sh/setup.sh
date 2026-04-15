#!/bin/bash

echo "Updating system..."
sudo apt update && sudo apt upgrade -y

echo "Installing essentials..."
sudo apt install -y git curl zip unzip ca-certificates gnupg

echo "Installing PHP 8.2 + extensions..."
sudo apt install -y php php-cli php-fpm php-mysql php-curl php-zip php-mbstring php-xml php-gd php-bcmath php-tokenizer php-json php-common

echo "Installing Composer..."
curl -sS https://getcomposer.org/installer | php
sudo mv composer.phar /usr/local/bin/composer

echo "Installing Node.js 18..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

echo "Installing MySQL Server..."
sudo apt install -y mariadb-server
sudo service mariadb start

echo "Installing Redis..."
sudo apt install -y redis-server
sudo service redis-server start

echo "Cloning your GitHub repo..."
git clone https://github.com/oselottiale/panel ~/panel
cd ~/panel

echo "Installing Composer dependencies..."
composer install --no-interaction --prefer-dist

echo "Installing Node dependencies..."
npm install
npm run build

echo "Setting up environment..."
cp .env.example .env
php artisan key:generate

echo "Creating database..."
sudo mysql -e "CREATE DATABASE panel;"
sudo mysql -e "CREATE USER 'ptero'@'localhost' IDENTIFIED BY 'ptero';"
sudo mysql -e "GRANT ALL PRIVILEGES ON panel.* TO 'ptero'@'localhost';"
sudo mysql -e "FLUSH PRIVILEGES;"

echo "Running migrations..."
php artisan migrate --force

echo "Setup complete!"
echo "Your Pterodactyl fork is ready in ~/panel"
