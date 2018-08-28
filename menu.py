import nuke
import traceback
import sendNodes_path as SP
import sendNodes_helper as SH

try:

	import sendNodes

	sendNodes_menu = nuke.menu("Nuke").addMenu("Scripts/Send Nodes")
	sendNodes_menu.addCommand("sendNodes", sendNodes.showMain, "", icon="")
	sendNodes_menu.addCommand("make screenshot", sendNodes.make_screenshot, "alt+a", icon="")
	sendNodes_menu.addCommand("open user folder", sendNodes.openUserFolder, "", icon="")

	nuke.addOnScriptLoad(sendNodes.updateNK)
	nuke.addOnScriptSave(sendNodes.updateNK)

except:
	f = open("%s/traceback_log.txt" % SP.GLOBAL_Folder, 'a')
	f.write("error: %s\n" % SH.Current_User)
	traceback.print_exc(file=f)
	f.flush()
	f.close()

