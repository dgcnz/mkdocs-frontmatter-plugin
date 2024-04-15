from mkdocs.plugins import BasePlugin
from mkdocs_frontmatter_plugin.config import FrontMatterConfig
from mkdocs_roamlinks_plugin.plugin import ROAMLINK_RE, RoamLinkReplacer
import re

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

        table = self.construct_table(front_matter_dict, config["docs_dir"], page.file.src_path)

        # Prepend the table to the Markdown content
        updated_markdown = table + markdown

        return updated_markdown

    def construct_table(self, front_matter_dict, base_docs_url, page_url):
        table = "| **Properties** |  |\n"
        table += "| --- | --- |\n"
        for key, value in front_matter_dict.items():
            # escape pipes in values unless it's a markdown link
            if re.match(ROAMLINK_RE, str(value)):
                value = re.sub(ROAMLINK_RE, RoamLinkReplacer(base_docs_url, page_url), str(value))
            else:
                value = str(value).replace("|", "\\|")
            table += f"| {key} | {value} |\n"
        table += "\n"
        return table
