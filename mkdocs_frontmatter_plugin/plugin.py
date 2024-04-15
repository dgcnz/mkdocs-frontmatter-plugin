from mkdocs.plugins import BasePlugin
from mkdocs_frontmatter_plugin.config import FrontMatterConfig


class FrontMatterPlugin(BasePlugin[FrontMatterConfig]):
    supports_multiple_instances = True

    # Initialize plugin
    def on_config(self, config):
        if not self.config.enabled:
            return

    def on_page_markdown(self, markdown, page, config, **kwargs):
        if not self.config.enabled:
            return

        front_matter_dict = page.meta

        # Construct table from front matter data
        if self.config.attributes:
            front_matter_dict = {
                k: v
                for k, v in front_matter_dict.items()
                if k in self.config.attributes
            }

        table = self.construct_table(front_matter_dict)

        # Prepend the table to the Markdown content
        updated_markdown = table + markdown

        return updated_markdown

    def construct_table(self, front_matter_dict):
        table = "| **Properties** |  |\n"
        table += "| --- | --- |\n"
        for key, value in front_matter_dict.items():
            # escape pipes in values
            value = str(value).replace("|", "\\|")
            table += f"| {key} | {value} |\n"
        table += "\n"
        return table
