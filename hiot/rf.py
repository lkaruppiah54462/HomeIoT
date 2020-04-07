
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 22:45:40 2020
Company : LK Consulting
@author: LK
"""

from app import app

if __name__ == "__main__":
    #socketio.run(app, host='0.0.0.0')
    app.run(host='0.0.0.0') 