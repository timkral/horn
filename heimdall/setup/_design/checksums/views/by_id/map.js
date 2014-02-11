function(doc) {
  emit(doc._id, {checksum: doc.checksum});
}