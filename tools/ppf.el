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
	 (html-file-name (replace-regexp-in-string "muse" "html" buffer-file-name)))
    (muse-publish-file buffer-file-name
		       "d-html-derive"
		       ppf/publish-dir
		       t)
    html-file-name))

(defun ppf/article-publish-view ()
  "To see the published file."
  (interactive)
  (let* ((html-file-name (ppf/article-publish)))
    (browse-url-firefox html-file-name)))


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


;;; Reporting

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
    
(define-key muse-mode-map [?\C-c ?p ?v] 'ppf/article-publish)
(define-key muse-mode-map [?\C-c ?p ?u] 'ppf/article-update)
(define-key muse-mode-map [?\C-c ?p ?i ?u] 'ppf/article-update)
(define-key python-mode-map [?\C-c ?p ?u] 'ppf/upload-this-file)

(provide 'ppf)
