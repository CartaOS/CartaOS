# CartaOS Troubleshooting Guide

This guide helps resolve common issues when installing, configuring, or using CartaOS.

## Installation Issues

### Linux Package Installation

#### .deb Package Issues
```bash
# If installation fails due to dependencies
sudo apt update
sudo apt install -f
sudo dpkg -i CartaOS_0.1.0_amd64.deb

# If WebKit dependencies are missing
sudo apt install libwebkit2gtk-4.0-dev libssl-dev
```

#### .rpm Package Issues
```bash
# For Fedora/RHEL systems
sudo dnf install CartaOS-0.1.0-1.x86_64.rpm

# If dependencies are missing
sudo dnf install webkit2gtk3-devel openssl-devel
```

#### AppImage Issues
```bash
# Make AppImage executable
chmod +x CartaOS_0.1.0_amd64.AppImage

# If FUSE is not available
./CartaOS_0.1.0_amd64.AppImage --appimage-extract-and-run
```

### System Requirements

#### Minimum Requirements Not Met
- **RAM**: Ensure at least 4GB available memory
- **Storage**: Verify 100MB+ free disk space
- **Graphics**: Modern graphics drivers required for WebKit rendering

#### Missing System Libraries
```bash
# Ubuntu/Debian
sudo apt install libgtk-3-0 libwebkit2gtk-4.0-37 libssl1.1

# Fedora/RHEL
sudo dnf install gtk3 webkit2gtk3 openssl-libs
```

## Configuration Issues

### API Key Problems

#### Invalid Gemini API Key
1. **Verify Key Format**: Ensure the API key is correctly copied from Google AI Studio
2. **Check Permissions**: Verify the API key has Gemini API access enabled
3. **Test Connection**: Use the Settings view to test the connection

#### Environment Variable Issues
```bash
# Check if .env file exists in the correct location
ls -la ~/.config/cartaos/.env

# Verify environment variable format
cat ~/.config/cartaos/.env
# Should contain: GEMINI_API_KEY=your_actual_key_here
```

### Obsidian Vault Configuration

#### Vault Path Not Found
1. **Verify Path**: Ensure the vault path exists and is accessible
2. **Permissions**: Check read/write permissions for the vault directory
3. **Absolute Path**: Use absolute paths (e.g., `/home/user/Documents/MyVault`)

#### File Access Issues
```bash
# Check vault directory permissions
ls -la /path/to/your/vault

# Fix permissions if needed
chmod -R 755 /path/to/your/vault
```

## Runtime Issues

### Application Won't Start

#### Missing Dependencies
```bash
# Check for missing libraries
ldd /usr/bin/cartaos

# Install missing dependencies
sudo apt install --fix-missing
```

#### Permission Errors
```bash
# Check application permissions
ls -la /usr/bin/cartaos

# Fix if needed
sudo chmod +x /usr/bin/cartaos
```

### Processing Issues

#### OCR Not Working
1. **File Format**: Ensure documents are in supported formats (PDF, images)
2. **File Size**: Large files may require more processing time
3. **Image Quality**: Poor quality scans may produce inaccurate OCR results

#### Summarization Failures
1. **API Connection**: Verify internet connectivity
2. **API Limits**: Check if you've exceeded Gemini API quotas
3. **Document Size**: Very large documents may hit API limits

#### File Queue Issues
1. **Directory Permissions**: Ensure CartaOS can read the configured directories
2. **File Locks**: Close files in other applications before processing
3. **Disk Space**: Verify sufficient space for temporary processing files

### Performance Issues

#### Slow Processing
1. **System Resources**: Close unnecessary applications to free RAM
2. **Network Speed**: Slow internet affects AI summarization
3. **Document Complexity**: Complex layouts take longer to process

#### High Memory Usage
1. **Large Documents**: Process smaller batches of documents
2. **Background Processes**: Close other memory-intensive applications
3. **System Monitoring**: Use `htop` or similar to monitor resource usage

## Error Messages

### Common Error Codes

#### "Failed to load settings"
- **Cause**: Configuration file corruption or missing permissions
- **Solution**: Delete `~/.config/cartaos/settings.json` and reconfigure

#### "API request failed"
- **Cause**: Network issues or invalid API key
- **Solution**: Check internet connection and verify API key in Settings

#### "File not found"
- **Cause**: Configured paths don't exist or are inaccessible
- **Solution**: Verify all paths in Settings and check permissions

#### "Processing timeout"
- **Cause**: Document too large or complex for processing
- **Solution**: Try smaller documents or increase timeout in configuration

### Log Files

#### Accessing Logs
```bash
# Application logs location
~/.config/cartaos/logs/

# View recent logs
tail -f ~/.config/cartaos/logs/cartaos.log

# Search for specific errors
grep -i error ~/.config/cartaos/logs/cartaos.log
```

#### Debug Mode
```bash
# Start with debug logging
RUST_LOG=debug cartaos

# Or set environment variable permanently
echo 'export RUST_LOG=debug' >> ~/.bashrc
```

## Network Issues

### Firewall Configuration
```bash
# Allow outbound HTTPS (port 443) for API calls
sudo ufw allow out 443

# Check current firewall status
sudo ufw status
```

### Proxy Configuration
If behind a corporate proxy, set environment variables:
```bash
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
```

## Recovery Procedures

### Reset Configuration
```bash
# Backup current settings
cp -r ~/.config/cartaos ~/.config/cartaos.backup

# Remove configuration to reset
rm -rf ~/.config/cartaos

# Restart application to recreate defaults
cartaos
```

### Clean Reinstall
```bash
# Remove application
sudo apt remove cartaos  # or sudo dnf remove cartaos

# Remove configuration
rm -rf ~/.config/cartaos

# Reinstall
sudo dpkg -i CartaOS_0.1.0_amd64.deb
```

## Getting Help

### Before Reporting Issues
1. **Check Logs**: Review application logs for specific error messages
2. **System Info**: Note your OS version, available RAM, and disk space
3. **Reproduction**: Document steps to reproduce the issue
4. **Screenshots**: Include screenshots of error messages if applicable

### Reporting Bugs
Create an issue on GitHub with:
- Operating system and version
- CartaOS version
- Complete error message
- Steps to reproduce
- System specifications
- Log file excerpts (remove sensitive information)

### Community Support
- **GitHub Discussions**: General questions and community help
- **Documentation**: Check README.md and other documentation files
- **Issues**: Bug reports and feature requests

## Performance Optimization

### System Tuning
```bash
# Increase file descriptor limits for large document processing
ulimit -n 4096

# Monitor system resources
htop
iostat -x 1
```

### Application Settings
- **Batch Size**: Process smaller batches for better performance
- **Concurrent Processing**: Adjust based on system capabilities
- **Cache Settings**: Configure appropriate cache sizes for your use case
