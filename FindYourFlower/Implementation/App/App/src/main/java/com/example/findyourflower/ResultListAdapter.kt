package com.example.findyourflower

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import android.widget.Toast
import androidx.constraintlayout.widget.ConstraintLayout
import androidx.recyclerview.widget.RecyclerView
import org.w3c.dom.Text

class ResultListAdapter(
    val flowerTitleList: ArrayList<String>,
    val flowerPercentageList: ArrayList<String>,
    val flowerDescList: ArrayList<String>):
    RecyclerView.Adapter<ResultListAdapter.ViewHolder>() {
    override fun onCreateViewHolder(
        parent: ViewGroup,
        viewType: Int
    ): ViewHolder {
        val layoutInflater = LayoutInflater.from(parent.context)
        val listItem: View =
            layoutInflater.inflate(R.layout.result_object, parent, false)
        return ViewHolder(listItem)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.title.text = flowerTitleList[position]
        holder.percentage.text = flowerPercentageList[position]
        holder.desc.text = flowerDescList[position]
    }

    override fun getItemCount(): Int {
        return flowerTitleList.size
    }

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        var title: TextView
        var percentage: TextView
        var desc: TextView
        var constraintLayout: ConstraintLayout

        init {
            title = itemView.findViewById<View>(R.id.title) as TextView
            percentage = itemView.findViewById<View>(R.id.percent) as TextView
            desc = itemView.findViewById<View>(R.id.desc) as TextView
            constraintLayout =
                itemView.findViewById<View>(R.id.constraintLayout) as ConstraintLayout
        }
    }
}