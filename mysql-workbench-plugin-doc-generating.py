# MySQL Workbench Plugin

from wb import *
import grt
import mforms

ModuleInfo = DefineModule("ModelDocumentation", author="TheOwls", version="1.0.1", description="Generate Markdown documentation from a model for DevOps")

# This plugin takes no arguments
@ModuleInfo.plugin("info.theowls.wb.documentation", caption="Generate documentation (Markdown)", description="Creaates a Markdown for Devops from the DDM", input=[wbinputs.currentDiagram()], pluginMenu="Utilities")
@ModuleInfo.export(grt.INT, grt.classes.db_Catalog)
def documentation(diagram):

    textMain = "# Schema documentation\n\n\n"
    textHead = "### Tables:\n| Name | Use |\n| --- | --- |\n"
    textDetail = ""
    for figure in diagram.figures:
        if hasattr(figure, "table") and figure.table:
            textHead += "| [" + figure.table.name + "](#" + str.lower(figure.table.name) + ") | " + figure.table.comment + " |\n"
            textDetail += writeTableDoc(figure.table)

    textMain += textHead + "\n\n" + textDetail + "\n\n"
    mforms.Utilities.set_clipboard_text(textMain)
    mforms.App.get().set_status_text("Documentation generated into the clipboard. Paste it to your editor.")

    print ("Documentation is copied to the clipboard.")
    return 0

def writeTableDoc(table):
    text = '<a id="' + str.lower(table.name) + '"></a>\n## Table: `' + table.name + "`\n"

    if (len(table.comment)):
        text += "### Description: \n\n"
        text += table.comment + "\n\n"

    text += "| Column | Data type | Attributes | Default | Description |\n| --- | --- | --- | --- | ---  |\n"
    for column in table.columns:
        text += writeColumnDoc(column, table)

    text += "\n\n"

    return text


def writeColumnDoc(column, table):
    # column name
    text = "| `" + column.name + "`"

    # column type name
    if column.simpleType:
        text += " | " + column.simpleType.name
        # column max lenght if any
        if column.length != -1:
            text += "(" + str(column.length) + ")"
    else:
        text += " | "

    text += " | "

    # column attributes
    attribs = [];

    isPrimary = False;
    isUnique = False;
    for index in table.indices:
        if index.indexType == "PRIMARY":
            for c in index.columns:
                if c.referencedColumn.name == column.name:
                    isPrimary = True
                    break
        if index.indexType == "UNIQUE":
            for c in index.columns:
                if c.referencedColumn.name == column.name:
                    isUnique = True
                    break

    # primary?
    if isPrimary:
        attribs.append("PRIMARY")

    # auto increment?
    if column.autoIncrement == 1:
        attribs.append("Auto increments")

    # not null?
    if column.isNotNull == 1:
        attribs.append("Not null")

    # unique?
    if isUnique:
        attribs.append("Unique")

    text += ", ".join(attribs)

    # column default value
    text += " | " + (("`" + column.defaultValue + "`") if column.defaultValue else " ")

    # column description
    text += " | " + (nl2br(column.comment) if column.comment else " ")

    # foreign key
    for fk in table.foreignKeys:
        if fk.columns[0].name == column.name:
            text +=  ("<br /><br />" if column.comment else "") + "**foreign key** to column `" + fk.referencedColumns[0].name + "` on table `" + fk.referencedColumns[0].owner.name + "`."
            break


    # finish
    text  +=  " |" + "\n"
    return text


def writeIndexDoc(index):

    # index name
    text = "| " + index.name

    # index columns
    text += " | " + ", ".join(map(lambda x: "`" + x.referencedColumn.name + "`", index.columns))

    # index type
    text += " | " + index.indexType

    # index description
    text += " | " + (nl2br(index.comment) if index.comment else " ")

    # finish
    text += " |\n"

    return text

def nl2br(text):
    return "<br />".join(map(lambda x: x.strip(), text.split("\n")))

