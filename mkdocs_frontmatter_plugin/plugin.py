from mkdocs.plugins import BasePlugin
from mkdocs_frontmatter_plugin.config import FrontMatterConfig
from mkdocs_roamlinks_plugin.plugin import ROAMLINK_RE, RoamLinkReplacer
from mkdocs.plugins import get_plugin_logger
import re

# links are strings that start with http or https
HYPERLINK_PATTERN = re.compile(r'^https?://')
class FrontMatterPlugin(BasePlugin[FrontMatterConfig]):
    supports_multiple_instances = True

    # Initialize plugin
    def on_config(self, config):
        if not self.config.enabled:
            return

    def on_page_markdown(self, markdown, page, config, **kwargs):
        if not self.config.enabled:
            return

        front_matter_dict: dict = page.meta

        # Construct table from front matter data
        if self.config.attributes:
            front_matter_dict = {
                k: v
                for k, v in front_matter_dict.items()
                if k in self.config.attributes
            }
        if self.config.exclude:
            front_matter_dict = {
                k: v
                for k, v in front_matter_dict.items()
                if k not in self.config.exclude
            }

        base_docs_url = config["docs_dir"]
        page_url = page.file.src_path
        table = self.construct_table(front_matter_dict, config["docs_dir"], page.file.src_path)

        # Prepend the table to the Markdown content
        updated_markdown = table + markdown

        return updated_markdown
    
    def hyperlink_replacer(self, element: str):
        if HYPERLINK_PATTERN.match(element):
            return f"[{element}]({element})"
        return element
    
    def process_string(self, string: str, base_docs_url: str, page_url: str):
        string = self.hyperlink_replacer(string)
        if re.match(ROAMLINK_RE, string):
            new_string = re.sub(ROAMLINK_RE, RoamLinkReplacer(base_docs_url, page_url), string)
            if string == new_string:
                # if the string is a roam link but the replacer didn't do anything, then it's a broken link
                # so we should just return the string inside
                string = re.search(ROAMLINK_RE, string).group(1)
            else:
                string = new_string
            string = string.replace("|", "\\|")
        return string


    def construct_table(self, front_matter_dict, base_docs_url, page_url):
        if not front_matter_dict:
            return ""
        table = "| **Properties** |  |\n"
        table += "| --- | --- |\n"
        kwargs = {
            "base_docs_url": base_docs_url,
            "page_url": page_url
        }
        for key, value in front_matter_dict.items():
            # if value is None or empty string, skip
            if not value:
                continue
            if isinstance(value, list):
                value = ", ".join([self.process_string(str(x),**kwargs) for x in value])
            elif isinstance(value, str):
                value = self.process_string(value, **kwargs)
            # check if value is a list
            table += f"| {key} | {value} |\n"
        table += "\n"
        return table


log = get_plugin_logger(__name__)