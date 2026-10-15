import re
import os
"""Page copy for the site. Setting and menu names match the app's own labels.

Values to bump at each release (the only place they live):
  REVIEWED_VERSION  the Library release the docs were last checked against
  REVIEWED_DATE     the "Last reviewed" date; None uses the build date
"""
import datetime

REVIEWED_VERSION = '1.6.1'
REVIEWED_DATE = None

# Set by build.py at build time: the latest releases from GitHub (or None when offline) and the Markdown converter.
RELEASES = None
to_html = None

LEFT = '<svg class="icon chevron" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="m15 6-6 6 6 6"/></svg>'


def release_page(page, r):
    """One page per large release: summary, sidebar contents, sections, download line, Related."""
    toc = [(re.sub(r'[^a-z0-9]+', '-', h.lower()).strip('-'), h) for h, _ in r['sections']]
    toc.append(('download', 'Download'))
    sections = []
    for h, items in r['sections']:
        sid = re.sub(r'[^a-z0-9]+', '-', h.lower()).strip('-')
        sections.append((sid, h, '<ul>' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'))
    tag = r['tag']
    download = (f'<p>Download Library {r["version"]} from the <a href="https://github.com/deansasek/library/releases/tag/{tag}" '
                'rel="noopener noreferrer">GitHub release page</a>, or install it with the command on the <a href="/install/">install page</a>.</p>')
    sections.append(('download', 'Download', download))
    return page('/whats-new/' + r['id'] + '/', f"What's new in Library {r['version']}", r['summary'], r['intro'], toc, sections,
                released=r['date'])


def render(page):
    out = {}

    # ---------- Guide ----------
    guide_toc = [
        ('get-started', 'Get started'), ('open-anything', 'Open anything'), ('quick-open', 'Quick Open'),
        ('quick-open-open-quick-open', 'Quick Open: Open Quick Open'), ('quick-open-search', 'Quick Open: Search'), ('quick-open-keyboard', 'Quick Open: Keyboard'),
        ('quick-open-actions', 'Quick Open: Actions'), ('quick-open-preview', 'Quick Open: Preview'), ('quick-open-settings-that-change-quick-open', 'Quick Open: Settings that change Quick Open'),
        ('quick-open-limits', 'Quick Open: Limits'), ('quick-open-what-it-stores-and-whether-it-syncs', 'Quick Open: What it stores and whether it syncs'), ('quick-open-notes', 'Quick Open: Notes'),
        ('clipboard', 'Clipboard'), ('clipboard-what-it-records', 'Clipboard: What it records'), ('clipboard-pin-an-item', 'Clipboard: Pin an item'),
        ('clipboard-open-the-clipboard-menu', 'Clipboard: Open the clipboard menu'), ('clipboard-paste-into-text-fields', 'Clipboard: Paste into text fields'), ('clipboard-paste-queue', 'Clipboard: Paste queue'),
        ('clipboard-copy-as', 'Clipboard: Copy as'), ('clipboard-markdown-links', 'Clipboard: Markdown links'), ('clipboard-filter-by-the-app-you-copied-from', 'Clipboard: Filter by the app you copied from'),
        ('clipboard-quick-look-and-the-space-key', 'Clipboard: Quick Look and the Space key'), ('clipboard-actions-for-text', 'Clipboard: Actions for text'), ('clipboard-play-copied-gifs', 'Clipboard: Play copied GIFs'),
        ('clipboard-lock-pinned-items', 'Clipboard: Lock pinned items'), ('clipboard-keep-clipboard-history-across-restarts', 'Clipboard: Keep clipboard history across restarts'), ('clipboard-settings', 'Clipboard: Settings'),
        ('clipboard-limits', 'Clipboard: Limits'), ('clipboard-what-it-stores-and-whether-it-syncs', 'Clipboard: What it stores and whether it syncs'), ('clipboard-caveats', 'Clipboard: Caveats'),
        ('save-snippets', 'Save snippets'), ('organize-your-library', 'Organize your library'), ('edit-an-item', 'Edit an item'),
        ('color-items', 'Color items'), ('the-library-menu', 'The Library menu'), ('add-notes', 'Add notes'),
        ('use-templates', 'Use templates'), ('read-later', 'Read later'), ('shortcuts', 'Shortcuts'),
        ('work-with-other-apps', 'Work with other apps'), ('stay-up-to-date', 'Stay up to date'), ('check-links', 'Check links'),
        ('back-up-and-restore', 'Back up and restore'), ('settings', 'Settings'), ('permissions', 'Permissions'),
        ('help-menu', 'Help menu'), ('troubleshooting', 'Troubleshooting'),
    ]
    guide = [
        ('get-started', 'Get started', '<p>Install Library first, then follow the first steps in <a href="/install/#first-steps">Install</a>.</p>'),
        ('open-anything', 'Open anything', '''<p>Bookmarks, apps, folders, and terminal commands open from the menu bar, a keyboard shortcut, or Spotlight. To open an item the other way, hold Option while you click it.</p>
<ul>
<li><strong>Bookmarks</strong> open in a new tab or a new window.</li>
<li><strong>Apps</strong> come to the front. To start a new copy, add a launch argument, such as <code>--profile work</code>.</li>
<li><strong>Terminal commands</strong> run in a login shell in a new Terminal window. Add only commands you trust.</li>
<li><strong>Folders</strong> open as submenus. Choose <strong>Open All</strong> in a folder to open its bookmarks and apps, one after another. Library skips dividers, terminal commands, templates, and apps that are no longer installed. It asks first when more than five items would open.</li>
</ul>'''),
        ('quick-open', 'Quick Open', '''<p>Quick Open is a search box that floats over your screen. It searches your library, your clipboard history, and your snippets, and it runs the result you choose.</p>'''),
        ('quick-open-open-quick-open', 'Open Quick Open', '''<ol><li>Press Control-Space. This is the default shortcut.</li><li>Type to search. The search field has the keyboard as soon as Quick Open opens.</li><li>Press Return, or click a row, to run it. Quick Open closes.</li></ol><p>Press the same shortcut again to close Quick Open without choosing anything. Quick Open also opens with the <code>library://search</code> address.</p><p>Quick Open appears centered on the screen under the pointer. It stays in place while you type. It appears over full-screen apps and on every Space.</p><p>To change the shortcut, go to <strong>Settings &gt; Shortcuts</strong> and change <strong>Show Quick Open</strong>. Control-Space can conflict with the macOS input source shortcut. If it does, pick another key combination.</p>'''),
        ('quick-open-search', 'Search', '''<p>Quick Open splits your text into words. Each word must match something about the item, and every word must match for the item to appear.</p><p>Library items and snippets are scored for each word:</p><table><thead><tr><th scope="col">Match</th><th scope="col">Score</th></tr></thead><tbody><tr><th scope="row">The start of the name, or the start of a keyword</th><td>4</td></tr><tr><th scope="row">Anywhere inside the name</th><td>3</td></tr><tr><th scope="row">Target, folder, or keywords (including the color)</th><td>2</td></tr><tr><th scope="row">The letters in order inside the name, with others between them</th><td>1</td></tr></tbody></table><p>An item's score is the sum of its word scores. Higher scores come first. Items with the same score are ordered by how often you have opened them, most first. Items you have not opened keep their order in the library.</p><p>Keywords, the item's color, and the folder name are all searched. Typing <code>red</code> finds items you gave the red color.</p><h3 id="quick-open-what-appears-with-an-empty-search">What appears with an empty search</h3><p>With the search field empty, Quick Open shows, in order:</p><ol><li><strong>Suggested</strong>: the link or app on the clipboard, or a link selected in the app in front, when it is not in your library yet. See <a href="#quick-open-add-a-suggested-link-or-app">Add a suggested link or app</a>.</li><li><strong>Frequently Used</strong>: up to five items you have opened at least twice.</li><li>The whole library, in the same order as the Library menu.</li><li><strong>Clipboard</strong>: the five first clipboard items. Pinned items come first.</li></ol><h3 id="quick-open-what-appears-with-a-search">What appears with a search</h3><p>With text in the search field, results appear in these groups, each with its own heading:</p><ul><li><strong>Top Hit</strong>: the first result. Return runs it.</li><li><strong>Library</strong>: matching items.</li><li><strong>Clipboard</strong>: up to eight matching clipboard items, pinned items first, then newest first.</li><li><strong>Snippets</strong>: matching snippets.</li><li><strong>Suggestions</strong>: a web address you typed, or a suggested link or app.</li></ul><p>Clipboard matches must contain every word, ignoring case. They are not ranked by score.</p><h3 id="quick-open-web-addresses">Web addresses</h3><p>If the search text is a web address, Quick Open adds two rows:</p><ul><li><strong>Open</strong> followed by the host, for example <code>Open example.com</code>.</li><li><strong>Add "example.com" to Library</strong>.</li></ul><p>A web address has no spaces. It is either a full address with <code>://</code>, or a host name with a dot and a top-level domain of at least two letters, such as <code>example.com/path</code>. <code>localhost</code> is not treated as a web address.</p><h3 id="quick-open-add-a-suggested-link-or-app">Add a suggested link or app</h3><p>When the clipboard holds a web link or an application that is not in your library, Quick Open offers to add it. It is listed under <strong>Suggested</strong> with an empty search. It is also listed when the search is at least two characters long and is part of the words "add to library", such as <code>ad</code> or <code>to li</code>.</p><p>A link selected in the app in front is used first, if Quick Open can read it. Choosing the suggestion adds it to the library. If the page can be read, Library names the new bookmark from its title when <strong>Name new bookmarks from their pages</strong> is on.</p><h3 id="quick-open-search-only-one-apps-copies">Search only one app's copies</h3><p>Type <code>from</code> and the name of an app to see only the clipboard items you copied while that app was in front. For example, <code>from Safari</code> shows Safari copies. Add words after the app name to search those copies, such as <code>from Safari invoice</code>.</p><p>The name must match an app that appears in your clipboard history, ignoring case. When two apps match, the longer name wins. When the search starts with <code>from &lt;app&gt;</code>, the library is not searched.</p>'''),
        ('quick-open-keyboard', 'Keyboard', '''<table><thead><tr><th scope="col">Key</th><th scope="col">What it does</th></tr></thead><tbody><tr><th scope="row">Up or Down arrow</th><td>Moves the selection. It stops at the first and last row.</td></tr><tr><th scope="row">Return or Enter</th><td>Runs the selected row. Quick Open closes, except when the row opens a submenu.</td></tr><tr><th scope="row">Option-Return</th><td>Opens a library item the other way. See the note below.</td></tr><tr><th scope="row">Command-1 to Command-9</th><td>Runs the first to ninth row. The number shows at the right of each row.</td></tr><tr><th scope="row">Tab</th><td>Shows the actions for the selected row. Tab again returns to the results.</td></tr><tr><th scope="row">Escape</th><td>Goes back one step: from a submenu to the actions, from the actions to the results, then closes Quick Open.</td></tr><tr><th scope="row">Space</th><td>Previews a clipboard item in Quick Look. See the note below.</td></tr></tbody></table><p>The pointer also works. Moving the pointer over a row selects it, once the pointer has moved. Clicking a row runs it. Right-clicking shows the same actions as Tab.</p><h3 id="quick-open-option-return">Option-Return</h3><p>For a library item that can open two ways, Option-Return does the opposite of the item's usual setting:</p><ul><li>A web bookmark opens in a new tab, or in a new window.</li><li>An app is brought forward, or a new instance is started.</li></ul><p>The labels in the actions list name the two ways. For clipboard items and snippets, Option-Return does the same as Return.</p><p>Option-click does not change how a row opens in Quick Open. Use Option-Return.</p><h3 id="quick-open-space">Space</h3><p>Space previews the selected clipboard item in Quick Look. Press Space again, or Escape, to close the preview.</p><p>Space types a space when the selected row is not a clipboard item, or when the clipboard item has nothing to preview. This is true even with an empty search.</p>'''),
        ('quick-open-actions', 'Actions', '''<p>Press Tab, or right-click a row, to see its actions. The actions depend on the row.</p><p><strong>Library item</strong> (a bookmark, app, command, or folder item):</p><ul><li><strong>Open</strong>, and the other way to open the item, where it applies.</li><li><strong>Copy Link</strong>, for a bookmark.</li><li><strong>Copy Clean Link</strong>, for a bookmark. It removes tracking parameters such as <code>utm_source</code>, <code>fbclid</code>, and <code>gclid</code>. The saved link is not changed.</li><li><strong>Copy as Markdown Link</strong>, for a bookmark. Not offered for templates.</li><li><strong>Copy Command</strong>, for a terminal command.</li><li><strong>Copy Path</strong> and <strong>Show in Finder</strong>, for an app.</li><li><strong>Add to Reading List</strong>, or <strong>Mark as Read</strong>, <strong>Mark as Unread</strong>, and <strong>Remove from Reading List</strong>, for a bookmark in the Reading List.</li></ul><p><strong>Clipboard item</strong>: see <a href="#clipboard">Clipboard</a>. The actions include Copy or Paste, Copy as Plain Text, Copy as, Quick Look, Pin or Unpin, Add to Paste Queue, Add to Library, and Delete.</p><p><strong>Typed web address</strong>: Copy Clean Link.</p><p><strong>Snippet</strong>: Copy and Edit.</p><p>Choosing an action runs it and closes Quick Open. Choosing <strong>Copy as…</strong> or another submenu lists its choices in place of the actions.</p>'''),
        ('quick-open-preview', 'Preview', '''<p>The right side of Quick Open shows the selected row in full. It is 280 points wide.</p><ul><li><strong>Clipboard text</strong>: the first 4,000 characters, selectable, with the source app, time, and size.</li><li><strong>Picture</strong>: the picture. A GIF plays.</li><li><strong>Files</strong>: each file's name and icon.</li><li><strong>Other copies</strong>: the number of formats.</li><li><strong>Library item</strong>: its name, icon, and link, command, or path. Its folder appears under it.</li><li><strong>Snippet</strong>: its name and the first 4,000 characters of its text.</li><li><strong>Locked pinned item</strong>: the words Pinned Item, and a <strong>Show Pinned Item</strong> button. See <a href="#clipboard-lock-pinned-items">Clipboard</a>.</li></ul><p>Clicking into the preview does not close Quick Open.</p>'''),
        ('quick-open-settings-that-change-quick-open', 'Settings that change Quick Open', '''<table><thead><tr><th scope="col">Setting</th><th scope="col">Where</th><th scope="col">Default</th><th scope="col">Effect</th></tr></thead><tbody><tr><th scope="row">Show Quick Open</th><td>Settings &gt; Shortcuts</td><td>Control-Space</td><td>The key that opens Quick Open.</td></tr><tr><th scope="row">Paste into text fields</th><td>Settings &gt; Clipboard</td><td>On</td><td>Clipboard items paste, not just copy, when a text field has the keyboard as Quick Open opens. Needs Accessibility access.</td></tr><tr><th scope="row">Require Touch ID or password to show pinned items</th><td>Settings &gt; Clipboard</td><td>Off</td><td>Locked pinned items show only as Pinned Item, and search does not find them.</td></tr><tr><th scope="row">Play copied GIFs</th><td>Settings &gt; Clipboard</td><td>Off</td><td>GIFs in the list and preview play.</td></tr><tr><th scope="row">Name new bookmarks from their pages</th><td>Settings &gt; General</td><td>Off</td><td>Suggested links are named from the page title.</td></tr></tbody></table><p>Keywords, colors, and notes on an item also affect what Quick Open shows. Notes appear under the item's name in the list.</p>'''),
        ('quick-open-limits', 'Limits', '''<ul><li>Clipboard matches in a search: eight.</li><li>Clipboard items with an empty search: five.</li><li>Frequently Used: five items, each opened at least twice.</li><li>Text in a clipboard item is searched up to its first 100,000 characters.</li><li>The preview shows the first 4,000 characters of text.</li><li>Each row is 42 points tall. The list shows about seven or eight rows at once and scrolls for the rest.</li></ul>'''),
        ('quick-open-what-it-stores-and-whether-it-syncs', 'What it stores and whether it syncs', '''<p>Quick Open stores nothing of its own. It reads:</p><ul><li>The library, which is in iCloud Drive when <strong>Keep Library in iCloud Drive</strong> is on.</li><li>Clipboard history, which stays on this Mac. See <a href="#clipboard">Clipboard</a>.</li><li>Snippets.</li><li>Open counts, which set the Frequently Used list, are kept on this Mac.</li></ul>'''),
        ('quick-open-notes', 'Notes', '''<ul><li>Quick Open closes when another app comes to the front, when the Spotlight search opens, or when you click elsewhere. It stays open while the Quick Look preview has the keyboard, and while the Touch ID or password prompt is up.</li><li>A row can be dragged into another app. A clipboard image, file, link, or text is dropped as that type, and Quick Open closes after the drop.</li></ul>'''),
        ('clipboard', 'Clipboard', '''<p>Library keeps a history of what you copy. You can copy an item back, paste it into a text field, pin the items you keep, and queue several items to paste in order. The history is reached from the clipboard menu, from the Clipboard submenu in the Library menu, and from Quick Open.</p>'''),
        ('clipboard-what-it-records', 'What it records', '''<p>Library records each copy with every format it was copied in, so copying an item back loses nothing. It records:</p><ul><li>Text, and links. A link is text that is a web address.</li><li>Images. A copied image is kept in one format, PNG when there is one.</li><li>Files, by name and icon.</li><li>Any other copy, which shows as Clipboard Item.</li></ul><p>Library checks the clipboard about twice a second. A copy appears in the history a moment after it is made.</p><p>Copying the same thing again does not add a second entry. The existing entry moves to the top, and keeps its pin.</p><p>Library does not record a copy when:</p><ul><li>The copy is marked as private by a password manager or a system field.</li><li>The copy is made while a password manager is in front. The apps are 1Password, Bitwarden, KeePassXC, LastPass, Dashlane, Keychain Access, and Passwords.</li><li>The copy is larger than 25 MB.</li></ul>'''),
        ('clipboard-pin-an-item', 'Pin an item', '''<p>Pinned items stay in the history after you quit, and they are never removed by the limits below.</p><ol><li>In Quick Open, find the item, and press Tab.</li><li>Choose <strong>Pin</strong>.</li><li>To remove the pin, press Tab on the item again and choose <strong>Unpin</strong>.</li></ol><p>Pins are set in Quick Open only. Pinned items show first in the clipboard menu, under <strong>Pinned</strong>, and first in Quick Open.</p>'''),
        ('clipboard-open-the-clipboard-menu', 'Open the clipboard menu', '''<ol><li>Press Control-Command-V. The menu opens at the pointer.</li><li>Choose an item to copy it back, or press a number key from 1 to 9 to choose one of the first nine items.</li><li>Hold Option over a rich-text item. Its entry changes to Copy as Plain Text, and choosing it copies the text without formatting.</li></ol><p>The menu lists pinned items under <strong>Pinned</strong> and the 20 most recent other items under <strong>Recent</strong>. It has <strong>Clear History</strong> at the bottom. When a text field has the keyboard, the headers say <strong>Paste Pinned</strong> and <strong>Paste Recent</strong>, and choosing an item pastes it. See <a href="#clipboard-paste-into-text-fields">Paste into text fields</a>.</p><p>If the clipboard or the selected text in the app in front holds a link or app that is not in your library, the menu starts with a row that adds it.</p><p>To change the shortcut, go to <strong>Settings &gt; Shortcuts</strong> and change <strong>Show Clipboard Menu</strong>.</p><h3 id="clipboard-the-clipboard-submenu-in-the-library-menu">The Clipboard submenu in the Library menu</h3><p>The Clipboard submenu in the Library menu lists the ten first items, pinned items first. Choosing one copies it. It never pastes. It has <strong>Clear History</strong>, and the paste queue when the queue has items.</p>'''),
        ('clipboard-paste-into-text-fields', 'Paste into text fields', '''<p>When <strong>Paste into text fields</strong> is on, choosing an item from Quick Open or the clipboard menu pastes it, if a text field had the keyboard when the menu or Quick Open opened. Otherwise it copies the item.</p><p>Library checks for a text field as the menu or Quick Open opens. When you then choose an item, Library presses Command-V in the app in front, a moment later.</p><p>This needs Accessibility access. Without it, choosing an item copies it.</p>'''),
        ('clipboard-paste-queue', 'Paste queue', '''<p>Use the paste queue to paste several items in order.</p><ol><li>In Quick Open, find an item, press Tab, and choose <strong>Add to Paste Queue</strong>.</li><li>Repeat for each item. The queue lists them in order in the clipboard menu.</li><li>Choose <strong>Paste Next</strong> in the clipboard menu. Library copies the first item and removes it from the queue.</li><li>Press Command-V in the app you are working in. Repeat from step 3 for the next item.</li></ol><p><strong>Clear Queue</strong> removes every item from the queue. The queue is kept in memory only, so it is empty when Library starts.</p><p>Choosing <strong>Paste Next</strong> copies the item. It does not paste it into the app for you.</p>'''),
        ('clipboard-copy-as', 'Copy as', '''<p>Copy as turns a text item into a new clipboard entry. The original stays in the history as it was.</p><ol><li>In Quick Open, find a text item, press Tab, and choose <strong>Copy as…</strong>.</li><li>Choose one of the options:<ul><li><strong>Plain Text</strong> copies the text without formatting.</li><li><strong>Trimmed Whitespace</strong> removes spaces and line breaks at both ends.</li><li><strong>Lowercase</strong> and <strong>Uppercase</strong> change the case.</li><li><strong>Joined Lines</strong> turns each line break into a space.</li><li><strong>Smart Punctuation</strong> turns straight quotes into curly quotes, <code>'</code> into <code>’</code>, <code>--</code> into an em dash, and <code>...</code> into an ellipsis. A quote opens when it comes first or follows a space, a bracket, or a dash. An apostrophe before a year, such as <code>'90s</code>, becomes <code>’90s</code>.</li></ul></li></ol><p>Copy as is offered for text items only. Links and pictures do not have it.</p>'''),
        ('clipboard-markdown-links', 'Markdown links', '''<p>Use Markdown links to paste a title and its address in a document.</p><ol><li>In Quick Open, find a bookmark, or a copied link, press Tab, and choose <strong>Copy as Markdown Link</strong>.</li><li>Paste into a Markdown document. The result is <code>[Title](address)</code>.</li></ol><p>The title is the bookmark's name, or the copied link's host. Characters that have a meaning in Markdown are escaped. Spaces and parentheses in the address are percent-encoded. In a rich-text field, the title pastes as a link.</p><p>Templates do not offer this action.</p>'''),
        ('clipboard-filter-by-the-app-you-copied-from', 'Filter by the app you copied from', '''<p>Each copy records the app that was in front when you copied it. You can list only the copies made in one app.</p><ol><li>Open Quick Open.</li><li>Type <code>from</code> and the app's name, such as <code>from Safari</code>.</li><li>Add words after the name to search those copies, such as <code>from Safari invoice</code>.</li></ol><p>The name matches an app in your history, ignoring case. Copies made while Library itself was in front have no app name, so they do not appear in any app filter.</p>'''),
        ('clipboard-quick-look-and-the-space-key', 'Quick Look and the Space key', '''<p>Quick Look shows a clipboard item in the system preview panel.</p><ul><li>In Quick Open, select a clipboard item and press Space. Press Space again, or Escape, to close the preview.</li><li>In Quick Open, press Tab, and choose <strong>Quick Look</strong>.</li></ul><p>Text and pictures are shown from a temporary copy. Files are shown where they are. Items with nothing to show, such as a format Library does not display, cannot be previewed.</p><p>The temporary copies are in a private folder in the system temporary folder. They are deleted when the preview closes. Any left by a quit or a crash are deleted the next time Library starts.</p><p>Clicking into the preview does not close Quick Open.</p>'''),
        ('clipboard-actions-for-text', 'Actions for text', '''<p>For a text item, Quick Open's Tab actions also include three actions that work on the text. Each appears only when the text has the matching thing in it:</p><ul><li><strong>Open in Maps</strong> opens an address in Apple Maps.</li><li><strong>Copy Phone Number</strong> copies the number with its digits and plus sign only.</li><li><strong>Add to Calendar</strong> opens Calendar's add-event sheet for a date or time. The event's title is the first line of the text. An event with no length lasts one hour.</li></ul><p>Library finds these on this Mac. It looks at the first 10,000 characters of the text.</p>'''),
        ('clipboard-play-copied-gifs', 'Play copied GIFs', '''<p>Browsers copy a still picture when you copy an animated GIF. With <strong>Play copied GIFs</strong> on, Library downloads the original GIF from the page, so it plays in the list and the preview.</p><ul><li>The setting is off by default.</li><li>It applies to copies made while it is on. It does not download GIFs for copies you made earlier.</li><li>Library asks the page's server for the GIF file only. It sends no cookies, and it stops after 10 seconds or 25 MB.</li><li>Animated GIFs show a small animated icon in the list.</li></ul><p>Turn it on in <strong>Settings &gt; Clipboard</strong>.</p>'''),
        ('clipboard-lock-pinned-items', 'Lock pinned items', '''<p>The lock asks for Touch ID or your Mac password before pinned items are shown or copied.</p><ol><li>Open <strong>Settings &gt; Clipboard</strong>.</li><li>Turn on <strong>Require Touch ID or password to show pinned items</strong>.</li></ol><p>Library will not turn the lock on when your Mac has neither Touch ID nor a password. Add a password in System Settings, then turn it on again.</p><p>With the lock on:</p><ul><li>A locked pinned item shows a lock icon and the words Pinned Item, in the list, the menu, and the queue.</li><li>Search does not find a locked pinned item.</li><li>Copying, Quick Look, Show Pinned Item, Add to Library, and Paste Next ask you to authenticate first. If you cancel, nothing changes, and the item stays locked.</li><li>Pin, Unpin, Delete, and Add to Paste Queue do not ask, and they do not show the item's text.</li></ul><p>After you authenticate, the items stay unlocked until one of these happens:</p><ul><li>You choose <strong>Lock Pinned Items</strong> in the Library menu. The item appears only when the lock is on, and it is dimmed while the items are already locked.</li><li>Your Mac goes to sleep.</li><li>You turn the setting on. Turning it on always locks the items.</li><li>Library quits. The next launch starts locked.</li></ul>'''),
        ('clipboard-keep-clipboard-history-across-restarts', 'Keep clipboard history across restarts', '''<p>By default, unpinned history is kept in memory and is gone when Library quits. Pinned items are always kept.</p><p>To keep unpinned history:</p><ol><li>Open <strong>Settings &gt; Clipboard</strong>.</li><li>Turn on <strong>Keep clipboard history across restarts</strong>.</li></ol><p>With this on:</p><ul><li>The unpinned history is saved to a file when a copy is made, about a second after it.</li><li>Copies from password managers and copies marked private are never saved.</li><li>Images over 5 MB are not saved. Other items are.</li><li>Turning the setting off deletes the saved history file.</li></ul><p>To copy the newest saved item to the clipboard when Library opens, turn on <strong>Put the Latest Item on the Clipboard When Library Opens</strong>. It needs the setting above. It does nothing when you have copied something since Library opened. A password copied before a restart could be pasted by someone else at this Mac.</p>'''),
        ('clipboard-settings', 'Settings', '''<table><thead><tr><th scope="col">Setting</th><th scope="col">Where</th><th scope="col">Default</th><th scope="col">Effect</th></tr></thead><tbody><tr><th scope="row">Keep clipboard history</th><td>Settings &gt; Clipboard</td><td>On</td><td>Records copies. Turning it off stops recording. Items already in the history stay until you quit or clear them.</td></tr><tr><th scope="row">Paste into text fields</th><td>Settings &gt; Clipboard</td><td>On</td><td>Choosing an item pastes it when a text field has the keyboard. Needs Accessibility access.</td></tr><tr><th scope="row">Play copied GIFs</th><td>Settings &gt; Clipboard</td><td>Off</td><td>Downloads the GIF behind a copied picture.</td></tr><tr><th scope="row">Require Touch ID or password to show pinned items</th><td>Settings &gt; Clipboard</td><td>Off</td><td>Locks pinned items.</td></tr><tr><th scope="row">Keep clipboard history across restarts</th><td>Settings &gt; Clipboard</td><td>Off</td><td>Saves unpinned history.</td></tr><tr><th scope="row">Put the Latest Item on the Clipboard When Library Opens</th><td>Settings &gt; Clipboard</td><td>Off</td><td>Copies the newest saved item at launch. Needs the setting above.</td></tr><tr><th scope="row">Remove tracking parameters when copying links</th><td>Settings &gt; General</td><td>On</td><td>When you copy a link from the history, removes tracking parameters such as <code>utm_source</code>, <code>fbclid</code>, and <code>gclid</code>. The saved link is not changed.</td></tr><tr><th scope="row">Show Clipboard Menu</th><td>Settings &gt; Shortcuts</td><td>Control-Command-V</td><td>Opens the clipboard menu.</td></tr></tbody></table><p><strong>Clear History</strong> in <strong>Settings &gt; Clipboard</strong> removes unpinned items. It is unavailable when every item is pinned.</p>'''),
        ('clipboard-limits', 'Limits', '''<ul><li>Unpinned items: the 50 most recent. Pinned items are not counted.</li><li>Memory: the history holds up to 200 MB in total, including pinned items. When the total is over, the oldest unpinned items are removed first.</li><li>Each copy: up to 25 MB. A larger copy is not recorded.</li><li>Search: the first 100,000 characters of each text item are searched.</li><li>Saved images: 5 MB each, when history is kept across restarts.</li><li>Clipboard menu: the first nine items have number keys. The menu lists pinned items, then up to 20 recent items.</li></ul>'''),
        ('clipboard-what-it-stores-and-whether-it-syncs', 'What it stores and whether it syncs', '''<ul><li><strong>Pinned items</strong> are saved in <code>~/.library/clipboard.json</code>.</li><li><strong>Unpinned history</strong> is saved in <code>~/.library/clipboard-history.json</code>, only when <strong>Keep clipboard history across restarts</strong> is on.</li><li>Both files are encrypted with a key kept in your login Keychain, on this Mac only.</li><li>The folder is readable only by you. Each file is readable only by you.</li><li>If a file cannot be read, it is moved aside, to <code>clipboard-damaged.bin</code> or <code>clipboard-history-damaged.bin</code>, and is not deleted.</li></ul><p>Clipboard history does not sync. It stays on this Mac, even with <strong>Keep Library in iCloud Drive</strong> on. Export does not include clipboard items.</p>'''),
        ('clipboard-caveats', 'Caveats', '''<ul><li>Turning off <strong>Keep clipboard history</strong> stops recording. It does not clear what is already in the history.</li><li>A copy is recorded about half a second after you make it.</li><li>Hold Option for Copy as Plain Text only works on rich-text items in the clipboard menu. Other items do not offer that choice.</li><li>The paste queue is cleared when Library quits.</li><li>Quick Look temporary copies are removed when Library starts, so a preview left open by a crash does not leave its copy behind.</li></ul>'''),
        ('save-snippets', 'Save snippets', '''<p>Save text you type often, such as an address or a standard reply, as a snippet. To add one, choose <strong>File &gt; New Snippet…</strong>, or click <strong>Snippets</strong> in the Library window.</p>
<p>To copy a snippet, type its name or a keyword in Quick Open, then press Return.</p>'''),
        ('organize-your-library', 'Organize your library', '''<p>Choose <strong>Edit Library…</strong> to manage everything in one window.</p>
<ul>
<li>Add items with the <strong>+</strong> menu. You can also drag an app or a link into the window.</li>
<li>Drag rows to reorder them, or to move them into a folder.</li>
<li>Select several rows to move, reorder, or edit them together. A bulk change is one undo step.</li>
<li>Deleted items go to <strong>Recently Deleted</strong>. They are removed for good after 30 days.</li>
<li>Right-click a row to open, edit or rename, move, share, or delete it. An app can also be shown in Finder.</li>
<li>To merge duplicate bookmarks, choose <strong>File &gt; Find Duplicates…</strong>.</li>
<li>To import bookmarks from Safari or Chrome, choose <strong>File &gt; Import Bookmarks…</strong>. They go into one folder. Press ⌘Z to undo the import.</li>
<li>To export or restore your whole library, use <strong>Settings &gt; General</strong>.</li>
</ul>
<p>Press ⌘Z to undo and ⇧⌘Z to redo.</p>'''),
        ('edit-an-item', 'Edit an item', '''<p>Select an item and press ⌘I. You can also choose <strong>Edit…</strong> from the toolbar or a right-click menu.</p>
<ul>
<li><strong>Name and icon.</strong> Pick an SF Symbol or an emoji, or keep the site's favicon or the app's icon.</li>
<li><strong>URL or Terminal Command</strong>, how a click opens it, and which browser to use.</li>
<li><strong>Keywords</strong> help Quick Open and Spotlight find the item.</li>
<li><strong>Color</strong> adds a dot to the item. See <a href="/guide/#color-items">Color items</a>.</li>
<li><strong>Shortcuts</strong> can be added to any item.</li>
<li><strong>Open When You Log In</strong> opens the item a few seconds after you log in.</li>
</ul>'''),
        ('color-items', 'Color items', '''<p>A color is a dot that helps you sort items at a glance. Use colors to organize your library, not to show status. Library has seven colors: red, orange, yellow, green, blue, purple, and gray.</p>
<ul>
<li><strong>Set a color.</strong> Select an item, press ⌘I to open Get Info, and choose a dot under <strong>Color</strong>. Choose the same dot again to clear it.</li>
<li><strong>Set a color on several items.</strong> Select them and edit them together. The sheet has a <strong>Color</strong> menu. Choose <strong>None</strong> to clear the color on all of them.</li>
<li><strong>See the color.</strong> The dot appears on the item's icon in the menu bar, in Quick Open, and in the Library window.</li>
<li><strong>Find colored items.</strong> Type the color's name in Quick Open, such as <code>blue</code>. Spotlight finds them by color name too.</li>
</ul>
<p>The color is saved with the item in <code>bookmarks.json</code>. If you keep your library in iCloud Drive, the color syncs to your other Macs with the item.</p>'''),
        ('the-library-menu', 'The Library menu', '''<p>Click the Library icon in the menu bar to open the menu. To open it at the pointer, press the Show Library Menu shortcut. <strong>Settings &gt; Shortcuts &gt; Library menu opens</strong> decides where it appears.</p>
<ul>
<li><strong>Update Available.</strong> Appears at the top when a newer version exists. Choose it to see the update options. See <a href="/guide/#stay-up-to-date">Stay up to date</a>.</li>
<li><strong>Your items.</strong> Bookmarks, apps, terminal commands, folders, and dividers, in the order you set in Edit Library. Folders open as submenus.</li>
<li><strong>Frequently Used.</strong> Up to five top-level items you have opened at least twice, most opened first.</li>
<li><strong>Reading List.</strong> Your bookmarks in the Reading List. Unread bookmarks show first.</li>
<li><strong>Clipboard.</strong> Your latest copies. Choose one to copy it again. When the history is empty, it says No Clipboard History. <strong>Clear History</strong> removes the unpinned history.</li>
<li><strong>Paste Queue.</strong> Appears when the queue has items. <strong>Paste Next</strong> pastes the next one, and <strong>Clear Queue</strong> empties it.</li>
<li><strong>Lock Pinned Items.</strong> Appears only when the Touch ID or password lock is on. It is dimmed while the pinned items are already locked.</li>
<li><strong>Edit Library…</strong>, <strong>Settings…</strong>, <strong>Open at Login</strong>, <strong>Check for Updates…</strong>, <strong>About Library</strong>, and <strong>Quit Library</strong>.</li>
</ul>
<p>A folder with nothing in it shows <strong>Empty</strong>. <strong>Open All</strong> opens the bookmarks and apps in the folder, including those in its subfolders, one after another. It is dimmed when none of them can be opened.</p>'''),
        ('add-notes', 'Add notes', '''<p>Write a note on any item in Get Info. Quick Open shows the note under the item's name. Spotlight includes it in the description. Notes are plain text and stay in your library.</p>'''),
        ('use-templates', 'Use templates', '''<p>Put <code>{}</code> in a URL where a value goes. Library asks for the value when you open the bookmark.</p>
<p>To name several values, use <code>{project}</code> or <code>{id:Issue number}</code>. Library asks for all of them in one sheet.</p>'''),
        ('read-later', 'Read later', '''<p>Add a bookmark to the Reading List from its right-click menu, or press Tab in Quick Open.</p>
<ul>
<li>The list appears in the Library window and in the menu. Unread bookmarks show first.</li>
<li>Mark a bookmark as read or unread, or remove it from the list.</li>
<li>Removing a bookmark from the list keeps it in your library.</li>
</ul>'''),
        ('shortcuts', 'Shortcuts', '''<p>A shortcut can be a key combination, a modified click, a scroll, a pinch, a swipe, or a hot corner. Shortcut keys need Control, Option, or Command. An item can have several shortcuts.</p>
<p>The default shortcuts are Control and right-click for the menu, Control-Space for Quick Open, and Control-Command-V for the clipboard menu. To change them, use <strong>Settings &gt; Shortcuts</strong>.</p>'''),
        ('work-with-other-apps', 'Work with other apps', '''<ul>
<li><strong>Spotlight</strong> finds your bookmarks, apps, and commands.</li>
<li><strong>Services:</strong> select a link in any app, then choose <strong>Services &gt; Add to Library</strong>. In Finder, select apps or folders and choose the same item.</li>
<li><strong>Share:</strong> right-click a bookmark or app and choose <strong>Share…</strong>. Drag a row into any app to drop its link or file.</li>
<li><strong>URL scheme:</strong> <code>library://open?name=Jira&amp;value=ABC-123</code> opens a bookmark and fills in its template. <code>library://menu</code> shows the menu. <code>library://search</code> opens Quick Open. Terminal commands can't be opened this way, so a web page can't run one.</li>
<li><strong>Shortcuts app:</strong> actions for opening and searching items, adding bookmarks and apps, Frequently Used, and the clipboard. Run Terminal Command always asks first. These actions appear only in a build that includes App Intents metadata, which Xcode generates. A build from <code>./build.sh</code> does not show them yet.</li>
</ul>'''),
        ('stay-up-to-date', 'Stay up to date', '''<p>While Library runs, it checks GitHub for a new release every hour. It also checks at launch if the last check was an hour or more ago.</p>
<p>When a newer version exists, one item appears at the top of the menu. Nothing pops up. To turn checks off, use <strong>Settings &gt; General</strong>. Choose <strong>Check for Updates…</strong> at any time. It offers the newer version. If you choose to install it, Library opens Terminal, clones the release, and runs its installer. It does not install silently. See <a href="/privacy/#what-is-sent">what is sent</a>.</p>'''),
        ('check-links', 'Check links', '''<p>Library can check that each bookmark's page is still there. It's off by default. To turn it on, use <strong>Settings &gt; General &gt; Check links periodically</strong>.</p>
<ul>
<li>Once a day while Library is open, Library quickly checks each bookmark. It doesn't download the page.</li>
<li>If a site doesn't answer that quick check, Library loads the page and reads only its first 64 KB.</li>
<li>Each bookmark is checked at most once a day.</li>
<li>A bookmark whose page is missing or can't be reached shows a warning in <strong>Edit Library</strong>.</li>
</ul>
<p>To check now, choose <strong>File &gt; Check Links</strong>.</p>'''),
        ('back-up-and-restore', 'Back up and restore', '''<p>Export saves your library to one file, and Restore brings it back. Both are in <strong>Settings &gt; General</strong>. You can also choose <strong>File &gt; Export Library…</strong>.</p>
<ul>
<li><strong>Export…</strong> saves your bookmarks, folders, shortcuts, icons, keywords, colors, templates, and Open at login settings to a JSON file named <code>Library Backup</code> with the date.</li>
<li><strong>Restore…</strong> opens a backup. Library shows how many items your library has and how many the backup has, then asks you to confirm. Choose <strong>Replace Library</strong> to continue. Cancel is the default button.</li>
<li><strong>Undo</strong> brings back the library you had before the restore.</li>
</ul>
<p>Clipboard items are not in a backup. Pinned clipboard items are encrypted with a key that stays on this Mac. Recently Deleted items in a backup stay deleted after a restore.</p>'''),
        ('settings', 'Settings', '''<p>Press ⌘, to open Settings. It has three tabs: General, Shortcuts, and Clipboard.</p>
<h3>General</h3>
<ul>
<li><strong>Open at login</strong> starts Library when you log in.</li>
<li><strong>Name new bookmarks from their pages</strong>. Library reads each new bookmark's title from its page. Until the title arrives, or when the page has none, the bookmark is named after its host. Off by default.</li>
<li><strong>Keep Library in iCloud Drive</strong>. See <a href="/privacy/#icloud-drive">iCloud Drive</a>. Off by default.</li>
<li><strong>Check for updates automatically</strong>. On by default. See <a href="/guide/#stay-up-to-date">Stay up to date</a>.</li>
<li><strong>Check links periodically</strong>. Off by default. See <a href="/guide/#check-links">Check links</a>.</li>
<li><strong>Export…</strong> and <strong>Restore…</strong> save and restore your library. See <a href="/guide/#back-up-and-restore">Back up and restore</a>.</li>
<li><strong>Show…</strong> opens the welcome screen, which explains Library, lists your shortcuts, and asks for access.</li>
<li><strong>Remove tracking parameters when copying links</strong>. On by default. Library removes tracking codes such as <code>utm_source</code>, <code>fbclid</code>, and <code>gclid</code> from a link you copy. The rest of the link stays the same, and the saved link is not changed.</li>
</ul>
<h3>Shortcuts</h3>
<ul>
<li><strong>Show Library Menu</strong>, <strong>Show Quick Open</strong>, <strong>Show Clipboard Menu</strong>, and <strong>Open Copied Link</strong>. Click a field and press the new keys. These work in every app. Open Copied Link opens the web link you last copied. A beep means the clipboard has no link.</li>
<li><strong>Library menu opens</strong>: <strong>At the Pointer</strong> or <strong>From the Menu Bar</strong>.</li>
<li><strong>Allow…</strong> asks for Accessibility access. Clicks, scrolls, pinches, swipes, and suggesting a selected link need it.</li>
<li><strong>Restore Defaults</strong> puts the shortcuts back to their defaults: Control and right-click for the Library menu, Control-Space for Quick Open, and Control-Command-V for the clipboard menu. macOS may use Control-Space to switch input sources.</li>
</ul>
<h3>Clipboard</h3>
<ul>
<li><strong>Keep clipboard history</strong>. On by default. Turn it off to stop recording new copies.</li>
<li><strong>Paste into text fields</strong>. On by default. If a text field has the keyboard, choosing an item pastes it. Otherwise it copies. This needs Accessibility access.</li>
<li><strong>Play copied GIFs</strong>. Off by default. See <a href="/privacy/#what-is-sent">What is sent</a>.</li>
<li><strong>Clear History</strong> removes the unpinned history.</li>
<li><strong>Keep clipboard history across restarts</strong>. Off by default. See <a href="/guide/#clipboard">Keep what you copy</a>.</li>
<li><strong>Put the Latest Item on the Clipboard When Library Opens</strong>. Off by default. The newest saved item is copied when Library opens, so you can paste it right away. A password copied before a restart could be pasted by someone else at this Mac.</li>
<li><strong>Require Touch ID or password to show pinned items</strong>. Off by default. See <a href="/privacy/#touch-id-lock">Touch ID or password lock</a>.</li>
</ul>'''),
        ('permissions', 'Permissions', '''<ul>
<li>Keyboard shortcuts, hot corners, Quick Open, and the menus don't need any permission.</li>
<li>Click, scroll, pinch, and swipe shortcuts, pasting into text fields, and suggesting a selected link need Accessibility access. Turn it on in <strong>System Settings &gt; Privacy &amp; Security &gt; Accessibility</strong>. Library reads your selection only when you open one of its menus, and it doesn't keep it.</li>
</ul>'''),
        ('help-menu', 'Help menu', '''<p>The Help menu is in the menu bar at the top of the screen.</p>
<ul>
<li><strong>Library Help</strong> opens the Library README on GitHub.</li>
<li><strong>Keyboard Shortcuts</strong> opens the shortcuts section of the README on GitHub.</li>
<li><strong>Welcome Tour…</strong> opens the welcome screen. It is the same as <strong>Settings &gt; General &gt; Show…</strong>.</li>
<li><strong>Report an Issue…</strong> opens a new issue on GitHub.</li>
</ul>
<p>The GitHub links open in your default browser. Library does not load them.</p>'''),
        ('troubleshooting', 'Troubleshooting', '''<ul>
<li><strong>A shortcut doesn't work.</strong> Another app may use the same keys. Check <strong>Settings &gt; Shortcuts</strong>. Control-Space can conflict with the macOS input source shortcut.</li>
<li><strong>Clicks stop working after a macOS update.</strong> Remove Library from Accessibility, then add it again.</li>
<li><strong>Open at Login does nothing.</strong> Move <code>Library.app</code> to <code>/Applications</code> first. The login item remembers where the app is.</li>
<li><strong>Services don't appear.</strong> Log out and back in, or run <code>/System/Library/CoreServices/pbs -update</code>.</li>
</ul>'''),
    ]
    out['/guide/index.html'] = page('/guide/', 'Library guide: features, settings, and permissions', 'Every feature, setting, and permission in Library.',
                                    'Every feature, setting, and permission in Library, with the steps to use each one.',
                                    guide_toc, guide)

    # ---------- Privacy ----------
    privacy_toc = [('what-is-stored', 'What is stored'), ('your-files', 'Your files'), ('what-is-sent', 'What is sent'),
                   ('touch-id-lock', 'Touch ID or password lock'), ('icloud-drive', 'iCloud Drive')]
    privacy = [
        ('what-is-stored', 'What is stored', '''<p>Library keeps your library and clipboard history on your Mac. Unpinned clipboard history stays in memory and is cleared when you quit, unless you turn on <strong>Keep clipboard history across restarts</strong> in <strong>Settings &gt; Clipboard</strong>. Only pinned items survive a quit otherwise.</p>
<p>Clipboard history never leaves your Mac.</p>'''),
        ('your-files', 'Your files', '''<p>Your files are in <code>~/.library/</code>:</p>
<table>
<caption>Files in ~/.library</caption>
<thead><tr><th scope="col">File</th><th scope="col">Contents</th></tr></thead>
<tbody>
<tr><th scope="row"><code>bookmarks.json</code></th><td>Your items, folders, shortcuts, and order</td></tr>
<tr><th scope="row"><code>clipboard.json</code></th><td>Pinned clipboard items, encrypted with a key kept in your Keychain</td></tr>
<tr><th scope="row"><code>clipboard-history.json</code></th><td>Unpinned clipboard history, encrypted the same way. This file exists only when <strong>Keep clipboard history across restarts</strong> is on. It is off by default.</td></tr>
<tr><th scope="row"><code>bookmarks-before-iCloud.json</code>, <code>bookmarks-iCloud-replaced.json</code></th><td>Backups kept when <strong>Keep Library in iCloud Drive</strong> is turned on, so no library is lost.</td></tr>
<tr><th scope="row"><code>bookmarks-damaged.json</code>, <code>snippets-damaged.json</code></th><td>A copy of a file that could not be read. Library tells you when it launches.</td></tr>
<tr><th scope="row"><code>snippets.json</code></th><td>Your snippets, as plain text. They are not encrypted, so don't keep passwords in a snippet.</td></tr>
<tr><th scope="row"><code>favicons/</code></th><td>Cached site icons. Library downloads them again if you delete the folder.</td></tr>
</tbody>
</table>
<p>Updates don't change your data.</p>'''),
        ('what-is-sent', 'What is sent', '''<p>Library connects to the internet only for these things.</p>
<ul>
<li><strong>Favicons</strong> (site icons) for the sites you bookmark.</li>
<li><strong>Copied GIFs</strong>, only if you turn on <strong>Play Copied GIFs</strong> in <strong>Settings &gt; Clipboard</strong>. It is off by default. Library downloads a GIF you copied from a web page so it can play.</li>
<li><strong>Link checks</strong>, only if you turn on <strong>Check links periodically</strong> in <strong>Settings &gt; General</strong>. It is off by default. Once a day, Library quickly checks that each bookmark's page is still there. It doesn't download the page. If a site doesn't answer that check, Library loads the page and reads only its first 64 KB.</li>
<li><strong>Smart titles</strong>, only if you turn on <strong>Name new bookmarks from their pages</strong> in <strong>Settings &gt; General</strong>. Library requests each new bookmark's page once and reads only the start of it to find the title.</li>
<li><strong>Update checks</strong> to <code>https://api.github.com/repos/deansasek/library/releases/latest</code>. This happens when you choose <strong>Check for Updates…</strong>, every hour while Library runs when automatic checks are on (the default), and at launch when the last check was an hour or more ago. The request names only the app's version, in its User-Agent header, and the ETag from GitHub's last answer. No account or other data is sent.</li>
<li><strong>Update in Terminal</strong>, only when you choose it. The release is cloned from <code>https://github.com/deansasek/library.git</code> into a temporary folder, which is deleted afterward.</li>
</ul>'''),
        ('touch-id-lock', 'Touch ID or password lock', '''<p>To lock pinned items, turn on <strong>Require Touch ID or password to show pinned items</strong> in <strong>Settings &gt; Clipboard</strong>. It is off by default.</p>
<p>Pinned items stay hidden until you authenticate. The unlock lasts until you choose <strong>Lock Pinned Items</strong>, your Mac sleeps, or Library quits. Search doesn't look inside locked items. If your Mac has no password or Touch ID, Library won't turn the lock on, and it explains how to add one.</p>'''),
        ('icloud-drive', 'iCloud Drive', '''<p>To keep your library in iCloud Drive, turn on <strong>Keep Library in iCloud Drive</strong> in <strong>Settings &gt; General</strong>. It is off by default.</p>
<p>Library moves <code>bookmarks.json</code> into the <code>Library</code> folder of iCloud Drive (<code>~/Library/Mobile Documents/com~apple~CloudDocs/Library/</code>) and links to it from <code>~/.library</code>. Your library then follows you to your other Macs. Clipboard history never leaves your Mac.</p>
<p>If two Macs change the library at the same time, the newer change wins for each item. Library tells you when a change from another Mac replaced an edit you hadn't saved.</p>
<h3>Temporary files</h3>
<p>Some files are written briefly to the system's temporary folder and then removed. A copy of a clip is written while you preview it in Quick Look. A terminal command is written as a script that deletes itself when Terminal runs it. A calendar event is written as an <code>.ics</code> file for Calendar. <strong>Export</strong> writes a backup file to the place you choose. It does not include clipboard items.</p>'''),
    ]
    out['/privacy/index.html'] = page('/privacy/', 'Privacy in Library: what is stored and sent', 'What Library stores, where it stores it, and what it sends over the network.',
                                      'What Library stores, where it stores it, and what it sends over the network.',
                                      privacy_toc, privacy)

    # ---------- Install ----------
    install_toc = [('requirements', 'Requirements'), ('install', 'Install'), ('first-steps', 'First steps'),
                   ('updates', 'Updates'), ('uninstall', 'Uninstall')]
    install = [
        ('requirements', 'Requirements', '''<dl class="requirements">
<div><dt>Operating system</dt><dd>macOS 26 or later</dd></div>
<div><dt>Developer tools</dt><dd>Xcode Command Line Tools</dd></div>
</dl>'''),
        ('install', 'Install', '''<p>Paste this into Terminal. It builds Library, puts <code>Library.app</code> in your Applications folder, and keeps the source code out of the way in Application Support.</p>
<div class="code-block"><pre><code>git clone https://github.com/deansasek/library.git "$HOME/Library/Application Support/Library/Source" &amp;&amp; "$HOME/Library/Application Support/Library/Source/install.sh"</code></pre></div>'''),
        ('first-steps', 'First steps', '''<ol>
<li>Press Control-Space to open Quick Open. Type a name and press Return.</li>
<li>Choose <strong>Edit Library…</strong> from the menu bar icon to add bookmarks and apps.</li>
<li>Turn on <strong>Open at Login</strong> in <strong>Settings &gt; General</strong> to start Library when your Mac starts.</li>
</ol>'''),
        ('updates', 'Updates', '''<p>Library checks for updates itself. <strong>Check for Updates…</strong> offers a newer version. If you choose to install it, Library opens Terminal, clones the release, and runs its installer. It does not install silently. Your library and pinned clipboard items are kept.</p>
<p>To update a clone made with the command above, run <code>update.sh</code> in the Source folder.</p>
<p>To learn how often Library checks, read <a href="/guide/#stay-up-to-date">Stay up to date</a>.</p>'''),
        ('uninstall', 'Uninstall', '''<ol>
<li>Quit Library.</li>
<li>Move <code>Library.app</code> from your Applications folder to the Trash.</li>
<li>Move the <strong>Library</strong> folder in <code>~/Library/Application Support</code> to the Trash. It holds the source you cloned.</li>
</ol>
<p>Your library and clipboard history stay in <code>~/.library</code>. Removing the app doesn't remove that folder. Move it to the Trash too if you want to delete your data.</p>'''),
    ]
    out['/install/index.html'] = page('/install/', 'Install Library on macOS with one command', 'Requirements, the one-command install, updates, and how to uninstall Library.',
                                      'Install Library with one command in Terminal. Requires macOS 26 or later.',
                                      install_toc, install)

    # ---------- Development ----------
    dev_toc = [('build', 'Build'), ('test', 'Test'), ('releasing', 'Releasing'), ('languages', 'Languages')]
    dev = [
        ('build', 'Build', '''<p>Run <code>./build.sh</code> to build the app.</p>
<p>On GitHub Actions, a pull request that changes code runs <code>./test.sh</code>. A push to <code>main</code> also builds the app and renders the screens. Changes to Markdown and <code>docs/</code> skip the run.</p>'''),
        ('test', 'Test', '''<p>Run <code>./test.sh</code> to run the checks in <code>Tests/</code>. The checks use private pasteboards and temporary files. They never touch your clipboard or your library.</p>'''),
        ('releasing', 'Releasing', '''<p>To publish a release, push a tag such as <code>vX.Y.Z</code>:</p>
<div class="code-block"><pre><code>git tag vX.Y.Z
git push origin vX.Y.Z</code></pre></div>
<p>Or run the <strong>Release</strong> workflow by hand and enter a version. Either way, GitHub Actions builds and checks the app, then publishes <code>Library-X.Y.Z.zip</code>. The zip holds only the source needed to build the app. Tests, workflows, docs, scripts, <code>test.sh</code>, and <code>update.sh</code> are left out.</p>
<p>If publishing fails with a server error, the workflow makes up to four attempts. Running it again is safe. It skips a release that already exists.</p>'''),
        ('languages', 'Languages', '''<p>Library is in English. The text lives in <code>Sources/Library/Resources/en.lproj/Localizable.strings</code>.</p>
<p>Write each user-facing string as <code>Text("…", bundle: L10n.bundle)</code>, or as <code>String(localized: "…", bundle: L10n.bundle)</code> where a <code>String</code> is needed. To add a string, add a line such as <code>"key" = "value";</code> with a <code>/* comment */</code> above it.</p>
<p>Dynamic text, such as file names, counts, and clipboard contents, isn't localized.</p>'''),
    ]
    out['/development/index.html'] = page('/development/', 'Building, testing, and releasing Library', 'Build, test, and release Library, and add languages.',
                                          'How to build, test, and release Library, and how text is localized.',
                                          dev_toc, dev)

    # ---------- Smart features ----------
    smart_toc = [('smart-actions', 'Smart actions'), ('smart-punctuation', 'Smart Punctuation'),
                 ('smart-titles', 'Smart titles'), ('smart-sorting', 'Smart sorting')]
    smart = [
        ('smart-actions', 'Smart actions', '''<p>If text has an address, a phone number, or a date, Library offers actions for it. Press Tab in Quick Open to see them: <strong>Open in Maps</strong>, <strong>Copy Phone Number</strong>, or <strong>Add to Calendar</strong>. Detection happens on your Mac.</p>'''),
        ('smart-punctuation', 'Smart Punctuation', '''<p>In <strong>Copy as</strong>, Smart Punctuation turns straight quotes and dashes into curly quotes, apostrophes, em dashes, and ellipses.</p>'''),
        ('smart-titles', 'Smart titles', '''<p>Turn on <strong>Name new bookmarks from their pages</strong> in <strong>Settings &gt; General</strong>. It is off by default. A new bookmark then takes the title of its page.</p>
<p>Library reads only the start of the page, and it requests each new bookmark's page once.</p>'''),
        ('smart-sorting', 'Smart sorting', '''<p>In the Edit Library window, open the sort menu in the header. Choose <strong>Most Used</strong> or <strong>Recently Opened</strong>.</p>'''),
    ]
    out['/smart-features/index.html'] = page('/smart-features/', 'Smart actions and smart titles in Library', 'Smart actions, Smart Punctuation, smart titles, and smart sorting in Library.',
                                             'Library works out what you copied and what you are doing. The next step is one choice away.',
                                             smart_toc, smart)

    # ---------- Releases ----------
    # No version or date here: the links always show the current release on GitHub.
    out['/releases/index.html'] = page('/releases/', 'Library releases: latest version and downloads', 'Download and read the notes for every Library release on GitHub.',
        'Release notes and downloads for every version of Library are on GitHub.',
        [], [], plain=True, extra=(
            '<ul class="links">'
            '<li><a href="https://github.com/deansasek/library/releases/latest" rel="noopener noreferrer">Get the Latest Release</a></li>'
            '<li><a href="https://github.com/deansasek/library/releases" rel="noopener noreferrer">See All Releases</a></li>'
            '</ul>'))

    # ---------- Accessibility ----------
    acc_toc = [('vision-and-motion', 'Motion and contrast'), ('keyboard', 'Keyboard'), ('voiceover', 'VoiceOver')]
    acc = [
        ('keyboard', 'Keyboard', """<p>Library works from the keyboard.</p>
<ul>
<li><strong>Control-Space</strong> opens Quick Open. Type to search, press <strong>↑</strong> or <strong>↓</strong> to move, and press <strong>Return</strong> to open the result. See <a href="/guide/#quick-open">Find it with Quick Open</a>.</li>
<li><strong>Tab</strong> opens a result the other way, or shows its other options.</li>
<li><strong>Space</strong> previews the selected item in Quick Look.</li>
<li><strong>Escape</strong> closes Quick Open.</li>
<li>In dialogs and sheets, <strong>Return</strong> confirms the default button, and <strong>Escape</strong> cancels.</li>
</ul>
<p>You can change the global keys in <a href="/guide/#shortcuts">Shortcuts</a>.</p>"""),
        ('voiceover', 'VoiceOver', """<p>Main controls have VoiceOver labels. Examples include <strong>Search Library</strong> in Quick Open, <strong>Actions</strong>, <strong>Sort</strong>, <strong>Add</strong>, <strong>Share</strong>, <strong>Delete</strong>, and <strong>Get Info</strong> in Edit Library.</p>
<p>Warnings about shortcuts that another app uses are labeled too.</p>
<p>To organize your library, see <a href="/guide/#organize-your-library">Organize your library</a>.</p>"""),
        ('report', 'Report a problem', """<p>If something in Library is hard to use with VoiceOver, the keyboard, or these settings, open an issue on the <a href="https://github.com/deansasek/library/issues" rel="noopener noreferrer">GitHub issues page</a>.</p>"""),
        ('vision-and-motion', 'Motion and contrast', """<ul>
<li><strong>Reduce Motion.</strong> When Reduce Motion is on, Quick Open's appearance animation is turned off. The Welcome screen does not animate between pages either.</li>
<li><strong>Increase Contrast.</strong> Quick Open uses system colors, which adapt to light and dark appearance and to Increase Contrast.</li>
</ul>
<p>Turn these on in <strong>System Settings</strong>. Library follows them.</p>"""),
    ]
    out['/accessibility/index.html'] = page('/accessibility/', 'Accessibility in Library: VoiceOver, keyboard, and motion',
        'How Library works with VoiceOver, the keyboard, Reduce Motion, and Increase Contrast.',
        'Library supports VoiceOver, keyboard use, Reduce Motion, and Increase Contrast. This page lists what the app does.',
        acc_toc, acc)

    # ---------- What's new ----------
    # Major and minor feature releases only. Data lives in content/whats_new.py.
    import importlib.util as _ilu
    _spec = _ilu.spec_from_file_location('whats_new', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'whats_new.py'))
    _wn = _ilu.module_from_spec(_spec)
    _spec.loader.exec_module(_wn)
    entries = ''
    for i, r in enumerate(_wn.RELEASES):
        badge = '<span class="badge">Latest</span>' if i == 0 else ''
        entries += (f'<section class="release"><h2><a href="/whats-new/{r["id"]}/">Library {r["version"]}</a></h2>'
                    f'<p class="updated">{r["date"]} {badge}</p><p>{r["summary"]}</p></section>')
    if not _wn.RELEASES:
        entries = '<p>No release notes yet.</p>'
    out['/whats-new/index.html'] = page('/whats-new/', "What's new in Library: release notes",
        'What each major and minor release of Library brings, newest first.',
        "What each major and minor release of Library brings, newest first.",
        [], [], plain=True, extra=entries + '<p class="links"><a href="https://github.com/deansasek/library/releases" rel="noopener noreferrer">See all releases on GitHub</a></p>')
    for r in _wn.RELEASES:
        out['/whats-new/' + r['id'] + '/index.html'] = release_page(page, r)

    # ---------- 404 ----------
    out['/404.html'] = ('<!doctype html>\n<html lang="en" dir="ltr">\n<head>\n<meta charset="utf-8">\n'
                        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
                        '<title>Page not found</title>\n<meta name="description" content="This page does not exist in Library.">\n'
                        '<meta name="robots" content="noindex">\n<link rel="canonical" href="https://deansasek.github.io/library-site/404.html">\n<meta property="og:title" content="Page not found">\n<meta property="og:url" content="https://deansasek.github.io/library-site/404.html">\n<meta property="og:description" content="This page does not exist in Library.">\n<meta property="og:image" content="https://deansasek.github.io/library-site/assets/icon.png">\n<meta property="og:image:alt" content="Library app icon">\n<meta name="twitter:card" content="summary">\n<link rel="icon" type="image/png" sizes="256x256" href="/assets/icon.png">\n'
                        '<link rel="stylesheet" href="/assets/styles.css">\n</head>\n<body>\n'
                        '<a class="skip-link" href="#main">Skip to content</a>\n'
                        + '__HEADER__' + '\n<main id="main" class="notfound"><h1>Page not found</h1>'
                        '<p class="subhead">This page doesn\'t exist.</p>'
                        '<p class="actions"><a class="button" href="/">Back to Library</a></p></main>\n'
                        + '__FOOTER__' + '\n</body>\n</html>\n')
    return out
