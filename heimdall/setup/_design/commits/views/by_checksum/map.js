function(doc) {
  if (doc.category == 'commit') {
    emit([doc.checksum, doc.category_sub], doc);
  }
}