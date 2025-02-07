#!/bin/bash
find /app/uploads -type f -mtime +1 -delete
find /app/outputs -type f -mtime +1 -delete
