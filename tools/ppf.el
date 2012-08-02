;;; === Using
;;; --------------------------------------------------------------
;; You will extract the source of ppf into 'ppf/root-dir. It's means that
;; you have to specify the directory of the source of ppf with
;; 'ppf/root-dir.


;;; TODO:
;; - Call from config.py
;; - Detect ftp is turn off


;; Dosen't work with "~"
(defcustom ppf/root-dir "/home/ptmono/Desktop/Documents/ppf/" "")
(defcustom ppf/post-dir (concat ppf/root-dir "tools/") "")
(defcustom ppf/publish-dir (concat ppf/root-dir "dbs/") "")
(defcustom ppf/publish-mode "d-html-derive" "")
(defcustom ppf/post-program (concat ppf/post-dir "post.py") "")
(defcustom ppf/cmd (concat ppf/post-dir "ppf_cmd.py") "")

;;(add-to-list 'load-path ppf/post-dir)

(defun ppf/pymacs-init ()
  (pymacs-exec "import sys")
  (pymacs-exec (concat "if '" ppf/post-dir
		       "' not in sys.path: sys.path.insert(0, '"
		       ppf/post-dir "')"))

  (pymacs-exec (concat "if '" ppf/root-dir
		       "' not in sys.path: sys.path.insert(0, '"
		       ppf/root-dir "')"))

  (pymacs-load "post" "ppf-")
  )
  
(defvar ppf/gnus-header-regexps
  '(("doc_id" "doc_id: \\([0-9]\\{10\\}\\)" 1)
    ("comment_id" "comment_id: \\([0-9]*\\)" 1)))

(defun ppf/gnus-get-info ()
  (let* ((group (car gnus-article-current))
	 (doc-id (cdr gnus-article-current))
	 (regexpls ppf/gnus-header-regexps)
	 (result (make-hash-table :test 'equal)))
    (with-temp-buffer
      (gnus-request-article-this-buffer doc-id group)
      (while regexpls
	(let* ((regexpl (car regexpls))
	       (name (car regexpl))
	       (regexp (car (cdr regexpl)))
	       (match-num (car (cdr (cdr regexpl))))
	       value)
	  (goto-char (point-min))
	  (re-search-forward regexp)
	  (setq value (match-string match-num))
	  (puthash name value result)
	  (setq regexpls (cdr regexpls)))))
    result))
	  

;; Fixme: pymacs returns http 500 error. But command is ok. What is the problem ?
(defun ppf/gnus-comment-delete ()
  (interactive)
  (ppf/pymacs-init)
  (let* ((info (ppf/gnus-get-info))
	 (doc-id (gethash "doc_id" info))
	 (comment-id (gethash "comment_id" info)))
    (ppf-deleteComment doc-id comment-id))
  )

;; Fixme: It must contains all the argument. Why?
(defun ppf/gnus-comment-reply ()
  (interactive)
  (ppf/pymacs-init)
  (let* ((info (ppf/gnus-get-info))
	 (doc-id (gethash "doc_id" info))
	 (content "fkdjlk abcdefg")
	 (name "dalsoo"))
    (ppf-writeComment doc-id content name "777"))
  )

;; It also 500 error.
(defun ppf/comment-delete2 ()
  (interactive)
  (ppf/pymacs-init)
  (let* ((info (ppf/gnus-get-info))
	 (doc-id (gethash "doc_id" info))
	 (comment-id (gethash "comment_id" info)))
    (pymacs-exec "import post")
    (pymacs-exec (format "post.deleteComment('%s', '%s')" doc-id comment-id)))
  )


(defun ppf/test ()
  (interactive)
  (ppf/pymacs-init)
  (let* ((info (ppf/gnus-get-info))
	 (doc-id (gethash "doc_id" info))
	 (comment-id (gethash "comment_id" info)))
    (condition-case nil
	;;(ppf-test doc-id comment-id)
      (error nil)))
  )


(defun ppf/article-publish ()
  "We need a method to convert the article to html before to
update the html of article."
  (interactive)
  (let* ((buffer-file-name (buffer-file-name))
	 (html-file-name (replace-regexp-in-string "muse" "html" buffer-file-name))
	 (doc-id (replace-regexp-in-string "\\.muse" "" (file-name-nondirectory buffer-file-name)))
	 html)
    (muse-publish-file buffer-file-name
		       "d-html-derive"
		       ppf/publish-dir
		       t)
    ;; Current css is of muse. Change of ppf.
    (ppf/pymacs-init)
    (setq html (ppf-getArticleHtml doc-id))
    (with-temp-file
	html-file-name
      (insert html))
      
    html-file-name))


(defun ppf/article-publish-view ()
  "To see the published file."
  (let* ((html-file-name (ppf/article-publish)))
    (browse-url-firefox html-file-name)))

(defun ppf/article-preview ()
  (interactive)
  (ppf/article-publish-view))


(defun ppf/article-update ()
  (interactive)
  (let* ((buffer-name (buffer-name))
  	 (doc-id (file-name-sans-extension buffer-name))
  	 ;; Get html. We translate the html of article not muse.
  	 (html-file-name (ppf/article-publish)))
    ;; We require html
    (ppf/article-publish)
    (ppf/pymacs-init)
    (ppf-updateArticle doc-id)
    (message "OK")
    ))


(defun ppf/article-check-html ()
  (let* ((buffer-file-name (buffer-file-name))
	 (html-file-name (replace-regexp-in-string "muse" "html" buffer-file-name)))
    (file-exists-p html-file-name)))


;; Fixme: I couldn't solve this. All is OK except this function.
;; post.updateFileWithFtp correctly act. But ppf/upload-this-file is not.
;; I couldn't found the reason. ppf/upload-this-file calls
;; post.updateFileWithFtp, but couldn't call uploader.uploadFile. I think
;; that it is the problem of pymacs.
;; (defun ppf/upload-this-file ()
;;   "Update current file to the server. The purpose is to change
;; the file of server such as server.py."
;;   (interactive)
;;   (let* ((absolute-file-path (buffer-file-name))
;; 	 (related-file-path (replace-regexp-in-string
;; 			     ppf/root-dir
;; 			     ""
;; 			     buffer-file-name)))
;;     (ppf/pymacs-init)
;;     (ppf-updateFileWithFtp related-file-path)))

(defun ppf/upload-this-file ()
  "I couldn't use this function with pymacs. I will use this
method befor I solve that."
  (interactive)
  (let* ((absolute-file-path (buffer-file-name))
  	 (related-file-path (replace-regexp-in-string
  			     ppf/root-dir
  			     ""
  			     buffer-file-name))
  	 (cmd (concat "python " ppf/cmd " uploadFile " related-file-path)))
    (shell-command-to-string cmd))
  (message "It looks like uploaded. I don't know. Make the stuff Hu~~."))


;;; === Reporting
;;; --------------------------------------------------------------

(defun ppf/dired-mark-unupdated-articles ()
  (interactive)
  (condition-case nil
      (unless (equal major-mode 'dired-mode)
	(error "ERROR: Only dired-mode")))
  (ppf/pymacs-init)
  (let* ((unupdated-lists (ppf-getUnupdatedArticles))
	 value)
    (save-excursion
      (while unupdated-lists
	(setq value (car unupdated-lists))
	(setq unupdated-lists (cdr unupdated-lists))
	(goto-char (point-min))
	(re-search-forward value)
	(dired-mark "*"))))
  )

(require 'json)

;;; ppf-report-doc-ids/

(defvar ppf-report-json)

(defun ppf-report-json/set ()
  (let* ((index-filename (ppf-indexFilename))
	 (json-key-type 'string))
    (setq ppf-report-json (json-read-file index-filename)))
  )

(defvar ppf-report-doc-ids)

(defvar ppf-report-doc-ids/public
  nil
  "It is used by other object. ppf-report-doc-ids/ has sortBy
  methods. The result will be stored in this variable.")

(defvar ppf-report-doc-ids/notPosted-public nil "")

(defvar ppf-report-doc-ids/regexp "[0-9]\\{10\\}")

(defun ppf-report-doc-ids/init ()
  (setq ppf-report-doc-ids (ppf-report-doc-ids/get))
  (setq ppf-report-doc-ids
	(ppf-report-doc-ids/sortStringToNumber ppf-report-doc-ids))
  (setq ppf-report-doc-ids/public ppf-report-doc-ids)

  (setq ppf-report-doc-ids/notPosted-public
	(ppf-report-doc-ids/getNotPosted))
  )

(defun ppf-report-doc-ids/sortStringToNumber (values)
  (sort values (lambda (a b) (> (string-to-number a) (string-to-number b)))))

(defun ppf-report-doc-ids/get ()
  (ppf/pymacs-init)
  (ppf-report-json/set)
  (let* ((content-json ppf-report-json)
	 (content-json-len (length content-json))
	 (counter 0)
	 doc-id
	 result)
    (while (< counter content-json-len)
      (setq doc-id (car (car content-json)))
      (setq content-json (cdr content-json))
      (setq result (cons doc-id result))
      (setq counter (+ counter 1)))
    result))


(defun ppf-report-doc-ids/getNotPosted ()
  "Get not posted article string numbers."
  (let* ((all-files (ppf-report-dired/getFileIds))
	 (posted-files ppf-report-doc-ids/public)
	 posted-file
	 )
    (while posted-files
      (setq posted-file (car posted-files))
      (setq posted-files (cdr posted-files))

      (setq all-files (remove posted-file all-files)))
    all-files)
  )


(defun ppf-report-doc-ids/sortByDocId ()
  (let* ((ids (ppf-report-doc-ids)))
    (setq ppf-report-doc-ids/public
	  (ppf-report-doc-ids/sortStringToNumber ids))
    ))




(defun ppf-report-doc-ids/sortByPublished ()
  )

(defun ppf-report-doc-ids/sortByUnpublished ()
  )



(defun ppf-report-doc-ids/isUnPublishedArticle (sid)
  (let* ((infos (cdr (assoc sid ppf-report-json)))
	 (result (cdr (assoc "unpublished" infos)))
	 )
    (if (equal result "")
	nil
      t
      ))
  )

;;; ppf-report-view/

(defcustom ppf-report/variables
  '(("title" 30 "Title")
    ("doc_id" 14 "ID")
    ("climit" 10 "Limit")
    )
  
    "")

(defun ppf-report/getKeys (nth)
  (let* ((key-lists ppf-report/variables)
	 key
	 result
	 )
    (while key-lists
      (setq key (nth nth (car key-lists)))
      (setq key-lists (cdr key-lists))

      (setq result (cons key result)))
    (setq result (reverse result))
    result)
  )

(defun ppf-report/getInfos (sid)
  "Get info list of id of document. It uses ppf-report/variables.
Each 0th element of list is the key of info. If
ppf-report/variables is

  '((\"title\" 30 \"Title\")
    (\"doc_id\" 14 \"ID\")
    (\"climit\" 10 \"Limit\"))

then the function will returns (list ('title value of if of
ppf-report-json' 'doc_id value of id of ppf-report-json' 'climit
value of id of ppf-report-json')
"
  (let* ((infos (cdr (assoc sid ppf-report-json)))
	 ;; Check unposted article
	 (infos (if infos
		    infos
		  (ppf-report/getUnPostedArticleInfos sid)))
	 (keys (ppf-report/getKeys 0))
	 key
	 value
	 result
	 )
    (while keys
      (setq key (car keys))
      (setq keys (cdr keys))
      (setq value (cdr (assoc key infos)))
      (setq result (cons value result)))
    (setq result (reverse result))
    result)
  )

(defun ppf-report/getUnPostedArticleInfos (sid)
  (ppf/pymacs-init)
  (let* ((json-key-type 'string)
	 result
	 )
    (setq result (json-read-from-string
		  (ppf-getArticleInfosAsJson sid)))
    result)
  )
   
(defun ppf-report-view ()
  (ppf-report-doc-ids/init)
  (ppf-report-view/insertHeader)
  (newline 2)
  (ppf-report-view/insertNotPostedArticles)
  (newline 2)
  (ppf-report-view/insertPostedArticles)
  )

(defun ppf-report-view/encode (values)
  (let* ((report-variables ppf-report/variables)
	 (keys-counter 0)
	 value
	 interval 			;For each value
	 separator
	 result)
    (while values
      (setq value (car values))
      (setq values (cdr values))
      (setq interval (nth 1 (nth keys-counter report-variables)))
      (setq value-len (length value))

      ;; Fix the length
      (if (> (+ value-len 2) interval)
	  (setq value (substring value 0 (- interval 2))))
	  
      (setq separator
	    (make-string (- interval (length value)) ? ))

      (setq result (concat result value separator))
      (setq keys-counter (+ keys-counter 1)))
    result)
  )

(defun ppf-report-view/insertHeader ()
  (let* ((headers (ppf-report/getKeys 2))
	 (result (ppf-report-view/encode headers)))
    (insert (concat "   " result)))
  )


(defun ppf-report-view/insertPostedArticles ()
  (let* ((ids ppf-report-doc-ids/public)
	 id
	 infos
	 line
	 unpublishedp
	 )
    (while ids
      (setq id (car ids))
      (setq ids (cdr ids))
      (setq infos (ppf-report/getInfos id))
      (setq line (ppf-report-view/encode infos))
      (setq unpublishedp (ppf-report-doc-ids/isUnPublishedArticle id))

      (if unpublishedp
	  (insert (concat " u " line))
	(insert (concat " - " line)))
      (newline)))
  )

(defun ppf-report-view/insertNotPostedArticles ()
  (let* ((ids ppf-report-doc-ids/notPosted-public)
	 id
	 infos
	 line
	 )
    
    (while ids
      (setq id (car ids))
      (setq ids (cdr ids))
      (setq infos (ppf-report/getInfos id))
      (setq line (ppf-report-view/encode infos))

      (insert (concat " v " line))
      (newline)))
  )
      
(defun ppf-report-view/getJsonKeys ()
  "Each element of ppf-report/variables has the key for json. Get
the list of key."
  (let* ((report-variables ppf-report/variables)
	 variable
	 result)
    (while report-variables
      (setq variable (car report-variables))
      (setq report-variables (cdr report-variables))
      (setq result (cons (nth 0 variable) result)))
    (setq result (reverse result))
    result)
  )



(defun ppf-report-dired/getFileIds ()
  (let* ((files (directory-files ppf/publish-dir nil ".*.muse"))
	 file
	 result
	 )
    (while files
      (setq file (car files))
      (setq files (cdr files))

      (if (string-match ppf-report-doc-ids/regexp file)
	  (setq result (cons (match-string 0 file) result))))
    (ppf-report-doc-ids/sortStringToNumber result))
  )
  


(defun ppf-report/jumpTo ()
  (interactive)
  (let* ((line-number (line-number-at-pos))
	 (len-of-notposted-articles (length ppf-report-doc-ids/notPosted-public))
	 (len-of-posted-articles (length ppf-report-doc-ids/public))
	 (notposted-article-line-offset 2)
	 (posted-article-line-offset 2)
	 (start-of-posted (+ notposted-article-line-offset
			     len-of-notposted-articles
			     posted-article-line-offset))
	 result
	 )
    (cond ((and (< notposted-article-line-offset line-number)
		(>= (+ notposted-article-line-offset len-of-notposted-articles)
		   line-number))
	   ;(message (number-to-string (- line-number (+ notposted-article-line-offset 1)))))
	   (setq result (- line-number (+ notposted-article-line-offset 1)))
	   (ppf-report/_jumpTo result t))
	  ((and (< start-of-posted line-number)
		(>= (+ start-of-posted len-of-posted-articles) line-number))
	   ;(message (number-to-string (- line-number (+ start-of-posted 1)))))
	   (setq result (- line-number (+ start-of-posted 1)))
	   (ppf-report/_jumpTo result))
	  )
    )
  )

(defun ppf-report/_jumpTo (nth &optional notPosted)
  (ppf/pymacs-init)
  (let* ((type (if notPosted
		   ppf-report-doc-ids/notPosted-public
		 ppf-report-doc-ids/public))
	 (sid (nth nth type))
	 (filename (ppf-getFilename sid)))
    (find-file filename))
  )

(defun ppf-report/jumpTo-notPosted (nth)
  (ppf/pymacs-init)
  (let* ((sid (nth nth ppf-report-doc-ids/notPosted-public))
	 (filename (ppf-getFilename sid)))
    (find-file filename))
  )
	 
  
(defun ppf-report ()
  (interactive)
  (if (get-buffer "*ppf-report*")
      (kill-buffer "*ppf-report*"))
  (switch-to-buffer (get-buffer-create "*ppf-report*"))
  (ppf-report-mode)
  (toggle-read-only)
  (highlight-current-line-minor-mode)
  (goto-line 2)
  )

(defvar ppf-report-mode-map
  (let ((map (make-sparse-keymap)))
    (suppress-keymap map)
    (define-key map [return] 'ppf-report/jumpTo)
    (define-key map [?\C-m] 'ppf-report/jumpTo)
    (define-key map [?f] 'ppf-report/jumpTo)
    (define-key map [?p] 'previous-line)
    (define-key map [?n] 'next-line)
    (define-key map [?g] 'ppf-report)
    map)
  "Keymap used by d-w3m-ytn-mode")


(define-derived-mode ppf-report-mode nil "Report ppf articles"
  ""
  (ppf-report-view)
  )






;;; === Keybinding
;;; --------------------------------------------------------------
(define-key muse-mode-map [?\C-c ?p ?p] 'ppf/article-publish)
(define-key muse-mode-map [?\C-c ?p ?v] 'ppf/article-preview)
(define-key muse-mode-map [?\C-c ?p ?u] 'ppf/article-update)
(define-key muse-mode-map [?\C-c ?p ?i ?u] 'ppf/article-update)
(define-key python-mode-map [?\C-c ?p ?u] 'ppf/upload-this-file)

(provide 'ppf)
