# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import google
from google.appengine.ext import vendor

lib_directory = os.path.dirname(__file__) + '/lib'

# Change where to find the google package (point to the lib/ directory)
google.__path__ = [os.path.join(lib_directory, 'google')] + google.__path__

# Add any libraries installed in the "lib" folder.
vendor.add('lib')
