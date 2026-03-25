#!/bin/bash

SPEECHD_CONF="/etc/speech-dispatcher/speechd.conf"
MODULES_DIR="/etc/speech-dispatcher/modules"

# Backup existing configuration
cp $SPEECHD_CONF "${SPEECHD_CONF}.bak"

cat <<EOL > $SPEECHD_CONF
# Speech Dispatcher configuration for Orca
AddModule "espeak-ng-generic"
AddModule "mbrola-generic"

# Set default voice and parameters
DefaultVoice "es"
DefaultRate 0
DefaultPitch 0
DefaultVolume 10
EOL

# Create or update module configurations
echo "Creating module configurations..."

# Example for mbrola
cat <<EOL > "$MODULES_DIR/mbrola-generic.conf"
# MBROLA configuration
GenericExecuteSynth "mbrola -e -t $DATA"
EOL

# Restart Speech Dispatcher service
echo "Restarting Speech Dispatcher..."
systemctl restart speech-dispatcher

echo "Configuration updated successfully. Please restart Orca for changes to take effect."
