from core.handler import Handler
from core.utils import *

import core.fileaction

import os
import re

class JDTUriResolver(Handler):
    name = "jdt_uri_resolver"
    method = "java/classFileContents"
    cancel_on_change = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lsp_location_link = None
        self.start_pos = None

    def process_request(self, uri, start_pos) -> dict:
        self.start_pos = start_pos
        self.lsp_location_link = uri
        return dict(uri=uri)

    def process_response(self, response: str):
        if not response:
            message_emacs("No definition found.")
            return

        if type(response) == str:
            # Save the analysis content to the file.
            external_file_name = re.match(r"jdt://contents/(.*?)/(.*)\.class\?", self.lsp_location_link).groups()[1].replace('/', '.') + ".java"
            external_file = os.path.join(self.file_action.lsp_server.library_directories[0], external_file_name)
            external_file_dir = os.path.dirname(external_file)
            os.makedirs(external_file_dir, exist_ok=True)
            if not os.path.exists(external_file):
                with open(external_file, 'w') as f:
                    f.write(response)

            # Jump to define in external file.
            self.file_action.lsp_server.message_queue.put({
                "name": "jump_to_external_file_link",
                "content": {
                    "filepath": external_file,
                    "file_action": self.file_action,
                    "lsp_location_link": self.lsp_location_link,
                    "start_pos": self.start_pos
                }
            })