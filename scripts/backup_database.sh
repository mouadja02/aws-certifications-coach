#!/bin/bash

# Database backup script for AWS Certifications Coach
# Usage: ./scripts/backup_database.sh

set -e

# Configuration
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="aws_coach_backup_${TIMESTAMP}.sql"
CONTAINER_NAME="aws-coach-db"
DB_NAME="aws_certifications"
DB_USER="awscoach"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting database backup...${NC}"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Check if container is running
if ! docker ps | grep -q "$CONTAINER_NAME"; then
    echo -e "${RED}Error: Database container is not running${NC}"
    exit 1
fi

# Perform backup
echo -e "${GREEN}Creating backup: ${BACKUP_FILE}${NC}"
docker exec -t "$CONTAINER_NAME" pg_dump -U "$DB_USER" -d "$DB_NAME" > "${BACKUP_DIR}/${BACKUP_FILE}"

# Compress backup
echo -e "${GREEN}Compressing backup...${NC}"
gzip "${BACKUP_DIR}/${BACKUP_FILE}"

# Calculate size
SIZE=$(du -h "${BACKUP_DIR}/${BACKUP_FILE}.gz" | cut -f1)
echo -e "${GREEN}Backup completed successfully!${NC}"
echo -e "File: ${BACKUP_DIR}/${BACKUP_FILE}.gz"
echo -e "Size: ${SIZE}"

# Clean up old backups (keep last 7 days)
echo -e "${YELLOW}Cleaning up old backups...${NC}"
find "$BACKUP_DIR" -name "aws_coach_backup_*.sql.gz" -mtime +7 -delete

echo -e "${GREEN}Backup process completed!${NC}"

