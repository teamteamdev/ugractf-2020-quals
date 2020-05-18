(ns ugractf.flag
  (:require
   [pandect.algo.sha256 :refer :all]))

(def PREFIX "ugra_good_languages_do_not_force_you_to_rely_on_bash_")
(def SECRET ["hazard-symbol-roots-birch"
             "algol-was-not-a-mistake"])
(def SALT [16 12])

(defn redeem-token [token]
  (apply str PREFIX
         (take (second SALT)
               (sha256-hmac token (second SECRET)))))
