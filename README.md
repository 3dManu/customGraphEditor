Maya用カスタムグラフエディターです。
ダウンロードは右上の緑色のClone or downloadのDownload zipからできると思います。
フォルダ名をcustomGraphEditor-masterからcustomGraphEditorに変更します。
customGraphEditorのフォルダごとmaya>scriptの中に入れたのちに下記コードをMayaのpythonで実行してください。

from customGraphEditor import UI

UI.main("bottom")

エラーなど改良してほしいところなどありましたら、issuesに書き込んでいただくか、twitterの@3D_manuあてにメッセージお願いします。

各種ツールの説明などはmanual.pdfに記載しています。
グラフエディタから切り離して使用したい場合はmainの引数を"float"に変更してください。

#####################################################

このスクリプトを使用して生じたトラブルや損害に関しましては作者は一切責任は負いません。 知人同士での再配布は問題ないですが、ネット等での再配布などはご遠慮ください。

#####################################################
